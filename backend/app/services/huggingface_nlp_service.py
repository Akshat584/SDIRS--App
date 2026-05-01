"""
HuggingFace NLP Service for SDIRS
Provides real sentiment analysis and text classification using HuggingFace Inference API.
"""
import os
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import httpx

from app.services.data_validator import DataValidator

logger = logging.getLogger("SDIRS_HuggingFace_NLP")

class HuggingFaceNLPService:
    """
    HuggingFace Inference API for real NLP analysis.
    Replaces keyword matching with transformer-based models.
    """

    # Model endpoints on HuggingFace
    SENTIMENT_MODEL = "distilbert-base-uncased-finetuned-sst-2-english"
    CLASSIFICATION_MODEL = "facebook/bart-large-mnli"

    def __init__(self, api_token: str = None):
        from app.core.config import settings
        self.api_token = api_token or os.getenv("HF_TOKEN") or settings.hf_token
        self.base_url = "https://api-inference.huggingface.co"
        self._fallback_enabled = True
        self._cache: Dict[str, Dict] = {}
        self._cache_max_size = 100

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for HuggingFace API requests."""
        headers = {"Content-Type": "application/json"}
        if self.api_token:
            headers["Authorization"] = f"Bearer {self.api_token}"
        return headers

    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment using DistilBERT.
        Returns sentiment label and confidence score.
        """
        if not text or not text.strip():
            return {
                "sentiment": "neutral",
                "score": 0.0,
                "confidence": 0.0,
                "source": "empty_input"
            }

        # Check cache
        cache_key = f"sentiment_{hash(text)}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        if not self.api_token:
            logger.warning("HF_TOKEN not configured, using fallback")
            return self._fallback_sentiment(text)

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Sentiment analysis
                sentiment_url = f"{self.base_url}/models/{self.SENTIMENT_MODEL}"
                resp = await client.post(
                    sentiment_url,
                    headers=self._get_headers(),
                    json={"inputs": text}
                )

                if resp.status_code == 200:
                    result = resp.json()
                    # Parse response - returns array of arrays
                    if result and len(result) > 0:
                        scores = result[0]
                        # Find highest scoring label
                        top_score = max(scores, key=lambda x: x.get("score", 0))
                        sentiment = top_score.get("label", "NEUTRAL").upper()

                        # Map to -1 to 1 scale
                        score_map = {
                            "POSITIVE": 0.7,
                            "NEGATIVE": -0.7,
                            "NEUTRAL": 0.0
                        }

                        response = {
                            "sentiment": sentiment.lower(),
                            "score": score_map.get(sentiment, 0.0),
                            "confidence": top_score.get("score", 0.85),
                            "source": "huggingface"
                        }

                        # Cache result
                        self._cache[cache_key] = response
                        return response

        except httpx.TimeoutException:
            logger.warning("HuggingFace API timeout, using fallback")
        except Exception as e:
            logger.error(f"HuggingFace API error: {e}")

        return self._fallback_sentiment(text)

    async def classify_text(self, text: str, categories: List[str] = None) -> Dict[str, Any]:
        """
        Classify text into disaster-related categories.
        Categories: alert, report, request, chatter, info
        """
        if not text or not text.strip():
            return {
                "classification": "chatter",
                "confidence": 0.0,
                "source": "empty_input"
            }

        if categories is None:
            categories = ["alert", "report", "request", "chatter", "information"]

        # Check cache
        cache_key = f"class_{hash(text)}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        if not self.api_token:
            return self._fallback_classification(text)

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                # Zero-shot classification
                classification_url = f"{self.base_url}/models/{self.CLASSIFICATION_MODEL}"
                resp = await client.post(
                    classification_url,
                    headers=self._get_headers(),
                    json={
                        "inputs": text,
                        "parameters": {"candidate_labels": ", ".join(categories)}
                    }
                )

                if resp.status_code == 200:
                    result = resp.json()
                    response = {
                        "classification": result.get("labels", ["chatter"])[0],
                        "confidence": result.get("scores", [0.0])[0],
                        "all_labels": result.get("labels", []),
                        "all_scores": result.get("scores", []),
                        "source": "huggingface"
                    }

                    self._cache[cache_key] = response
                    return response

        except Exception as e:
            logger.error(f"HuggingFace classification error: {e}")

        return self._fallback_classification(text)

    async def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Full NLP analysis: sentiment + classification.
        Combines both for the disaster triage pipeline.
        """
        # Sanitize input
        text = DataValidator.sanitize_user_input(text, max_length=1000)

        # Run both analyses
        sentiment = await self.analyze_sentiment(text)
        classification = await self.classify_text(text)

        # Determine signal strength based on classification
        high_priority_classes = ["alert", "request", "report"]
        signal_strength = 1.0 if classification["classification"] in high_priority_classes else 0.3

        # Override signal strength based on sentiment
        if sentiment["sentiment"] == "negative" and sentiment["score"] < -0.5:
            signal_strength = min(signal_strength * 1.5, 1.0)

        return {
            "classification": classification["classification"],
            "sentiment": sentiment["sentiment"],
            "sentiment_score": sentiment["score"],
            "confidence": (sentiment["confidence"] + classification["confidence"]) / 2,
            "signal_strength": signal_strength,
            "source": "huggingface" if sentiment["source"] == "huggingface" else "fallback"
        }

    def _fallback_sentiment(self, text: str) -> Dict[str, Any]:
        """Fallback sentiment analysis using keyword heuristics."""
        text_lower = text.lower()

        # Urgency indicators
        urgent_words = ["help", "sos", "trapped", "urgent", "emergency", "critical", "danger"]
        negative_words = ["fire", "flood", "dead", "injured", "destroyed", "damage", "crisis"]
        positive_words = ["safe", "okay", "resolved", "clear", "good"]

        urgency_score = sum(1 for w in urgent_words if w in text_lower) / len(urgent_words)
        neg_score = sum(1 for w in negative_words if w in text_lower) / len(negative_words)
        pos_score = sum(1 for w in positive_words if w in text_lower) / len(positive_words)

        if urgency_score > 0.2 or neg_score > 0.3:
            sentiment = "negative"
            score = -0.7 + (urgency_score * 0.3)
        elif pos_score > 0.3:
            sentiment = "positive"
            score = 0.5
        else:
            sentiment = "neutral"
            score = 0.0

        return {
            "sentiment": sentiment,
            "score": round(score, 2),
            "confidence": 0.6,
            "source": "fallback"
        }

    def _fallback_classification(self, text: str) -> Dict[str, Any]:
        """Fallback classification using keyword matching."""
        text_lower = text.lower()

        # Classification rules
        if any(w in text_lower for w in ["help", "sos", "trapped", "need", "save"]):
            return {
                "classification": "request",
                "confidence": 0.75,
                "source": "fallback"
            }
        elif any(w in text_lower for w in ["alert", "warning", "evacuate", "mandatory", "critical"]):
            return {
                "classification": "alert",
                "confidence": 0.8,
                "source": "fallback"
            }
        elif any(w in text_lower for w in ["fire", "flood", "smoke", "shaking", "earthquake", "water"]):
            return {
                "classification": "report",
                "confidence": 0.7,
                "source": "fallback"
            }
        elif any(w in text_lower for w in ["news", "update", "information", "official"]):
            return {
                "classification": "information",
                "confidence": 0.65,
                "source": "fallback"
            }

        return {
            "classification": "chatter",
            "confidence": 0.5,
            "source": "fallback"
        }

    def clear_cache(self):
        """Clear the analysis cache."""
        self._cache.clear()
        logger.info("NLP cache cleared")


# Global singleton
nlp_service = HuggingFaceNLPService()
