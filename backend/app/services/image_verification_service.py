import os
import logging
from app.core.config import settings
from app.services.disaster_cv_model import disaster_cv_service

logger = logging.getLogger("SDIRS_AI_Verification")

class ImageVerificationService:
    """
    SDIRS AI Incident Verification System (Module 3)
    Uses a specialized SDIRS Disaster CV model to analyze citizen-reported images.
    """
    
    @staticmethod
    async def analyze_incident_image(image_path: str) -> dict:
        """
        Analyzes an image using the Disaster CV Model to verify incident type and severity.
        """
        if not os.path.exists(image_path):
            logger.error(f"SDIRS AI: Image not found at {image_path}")
            return {"verified": False, "confidence": 0.0, "labels": [], "severity_boost": 0.0}

        try:
            # Use the disaster-specific CV model
            result = disaster_cv_service.analyze_image(image_path)

            
            logger.info(f"SDIRS AI Verified Incident: {result['labels']} with {result['confidence']*100:.1f}% confidence.")
            
            return result

        except Exception as e:
            logger.error(f"SDIRS AI Verification Error: {e}")
            return {"verified": False, "confidence": 0.0, "labels": [f"Error: {str(e)}"], "severity_boost": 0.0}
