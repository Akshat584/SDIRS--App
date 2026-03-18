import logging
import random
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger("SDIRS_NLP")

class BertTriageModel:
    """
    SDIRS NLP BERT Triage Model (Module 3/10)
    Simulates a BERT-based transformer model for classifying social media data.
    Provides sentiment analysis and incident signal extraction.
    """
    
    def __init__(self):
        self.model_name = "sdirs-bert-uncased-disaster-v2"
        self.last_update = datetime.now()
        logger.info(f"SDIRS AI: BERT Triage Model '{self.model_name}' initialized.")

    def analyze_text(self, text: str) -> Dict[str, Any]:
        """
        Simulates model inference on a piece of text.
        In production, this would use: inputs = tokenizer(text); outputs = model(**inputs)
        """
        text_lower = text.lower()
        
        # 1. Classification (Mocked BERT inference)
        classification = "chatter"
        if any(word in text_lower for word in ["help", "trapped", "sos", "save"]):
            classification = "request"
        elif any(word in text_lower for word in ["fire", "flood", "smoke", "shaking", "water"]):
            classification = "report"
        elif any(word in text_lower for word in ["alert", "warning", "evacuate", "critical"]):
            classification = "alert"

        # 2. Sentiment Analysis (Mocked)
        sentiment = 0.0
        if classification in ["request", "alert"]:
            sentiment = -0.8 + random.uniform(-0.1, 0.2) # Highly negative/urgent
        elif classification == "report":
            sentiment = -0.4 + random.uniform(-0.1, 0.1)
        else:
            sentiment = 0.1 + random.uniform(-0.2, 0.2)

        return {
            "classification": classification,
            "sentiment": round(sentiment, 2),
            "confidence": 0.85 + random.uniform(0.01, 0.1),
            "signal_strength": 1.0 if classification != "chatter" else 0.2
        }

# Global Singleton
nlp_service = BertTriageModel()
