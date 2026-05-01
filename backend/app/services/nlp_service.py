"""
SDIRS NLP Service (Module 3)
Wrapper that uses HuggingFace NLP service with fallback.
"""
import logging
from typing import Dict, Any

from app.services.huggingface_nlp_service import HuggingFaceNLPService

logger = logging.getLogger("SDIRS_NLP")

class BertTriageModel:
    """
    SDIRS NLP BERT Triage Model (Module 3/10)
    Uses HuggingFace Inference API for real transformer-based classification.
    Falls back to keyword heuristics when API unavailable.
    """

    def __init__(self):
        # Initialize HuggingFace service
        self.hf_service = HuggingFaceNLPService()
        self.model_name = "distilbert-base-uncased-finetuned-sst-2-english"
        self.last_update = None
        logger.info(f"SDIRS AI: BERT Triage Model initialized with HuggingFace")

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze text using HuggingFace transformers.
        Returns classification, sentiment, confidence, and signal strength.
        """
        import asyncio
        try:
            # Run async analysis
            result = asyncio.run(self.hf_service.analyze_text(text))
            self.last_update = result.get("timestamp")

            # Map to expected format for compatibility
            return {
                "classification": result.get("classification", "chatter"),
                "sentiment": result.get("sentiment", "neutral"),
                "confidence": result.get("confidence", 0.5),
                "signal_strength": result.get("signal_strength", 0.5),
                "source": result.get("source", "unknown")
            }
        except Exception as e:
            logger.error(f"NLP analysis error: {e}")
            # Return fallback
            return self._keyword_fallback(text)

    def _keyword_fallback(self, text: str) -> Dict[str, Any]:
        """Fallback using keyword matching."""
        text_lower = text.lower()

        # Classification
        classification = "chatter"
        if any(w in text_lower for w in ["help", "trapped", "sos", "save"]):
            classification = "request"
        elif any(w in text_lower for w in ["fire", "flood", "smoke", "shaking", "water"]):
            classification = "report"
        elif any(w in text_lower for w in ["alert", "warning", "evacuate", "critical"]):
            classification = "alert"

        # Sentiment
        sentiment = 0.0
        if classification in ["request", "alert"]:
            sentiment = -0.8
        elif classification == "report":
            sentiment = -0.4

        return {
            "classification": classification,
            "sentiment": sentiment,
            "confidence": 0.85,
            "signal_strength": 1.0 if classification != "chatter" else 0.2,
            "source": "fallback"
        }


# Global Singleton - replaces old nlp_service
nlp_service = BertTriageModel()
