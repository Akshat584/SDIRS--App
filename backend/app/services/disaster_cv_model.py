import os
import logging
from ultralytics import YOLO
from typing import List, Dict, Any
from app.core.config import settings

logger = logging.getLogger("SDIRS_DisasterCV")

class DisasterCVModel:
    """
    SDIRS Disaster-Specific Computer Vision Model.
    Wraps YOLOv8 and provides mapping from COCO classes to Disaster-relevant categories.
    """
    
    # Mapping COCO IDs/Labels to Disaster Categories
    # Note: Standard YOLOv8n has 80 COCO classes. Actual 'fire' detection
    # requires a custom trained model.
    DISASTER_MAPPING = {
        'boat': {
            'category': 'Flood/Water',
            'severity_weight': 0.7,
            'is_critical': False
        },
        'car': {
            'category': 'Traffic/Accident',
            'severity_weight': 0.4,
            'is_critical': False
        },
        'truck': {
            'category': 'Traffic/Accident',
            'severity_weight': 0.4,
            'is_critical': False
        },
        'bus': {
            'category': 'Traffic/Accident',
            'severity_weight': 0.5,
            'is_critical': False
        },
        'person': {
            'category': 'Human Activity',
            'severity_weight': 0.2,
            'is_critical': False
        }
    }

    def __init__(self, model_path: str = None):
        if model_path is None:
            model_path = settings.cv_model_path
        
        self.model = None
        try:
            # If the custom disaster model file doesn't exist, use the base yolov8n
            if not os.path.exists(model_path) and model_path != 'yolov8n.pt':
                logger.warning(f"SDIRS AI: Custom model {model_path} not found. Falling back to yolov8n.pt")
                model_path = 'yolov8n.pt'
            
            self.model = YOLO(model_path)
            logger.info(f"SDIRS AI: Disaster CV Model loaded ({model_path}).")
        except Exception as e:
            logger.error(f"SDIRS AI: Failed to load CV model: {e}")
            self.model = None

    @property
    def is_loaded(self) -> bool:
        return self.model is not None

    def analyze_image(self, image_input: Any) -> Dict[str, Any]:
        """
        Runs inference and maps detections to disaster-specific labels.
        image_input can be a file path (str) or bytes.
        """
        if self.model is None:
            return {"verified": False, "confidence": 0.0, "labels": ["Model Error"], "severity_boost": 0.0}

        try:
            # Handle bytes input by using PIL to open it
            if isinstance(image_input, bytes):
                from PIL import Image
                import io
                image_input = Image.open(io.BytesIO(image_input))

            # Run inference with configured confidence
            results = self.model(image_input, conf=settings.cv_confidence_threshold)

            
            detections = []
            max_conf = 0.0
            total_weight = 0.0
            disaster_labels = set()
            is_verified = False

            for r in results:
                for box in r.boxes:
                    cls_id = int(box.cls[0])
                    label = self.model.names[cls_id]
                    conf = float(box.conf[0])
                    
                    max_conf = max(max_conf, conf)
                    
                    # Map to disaster category if possible
                    mapping = self.DISASTER_MAPPING.get(label)
                    if mapping:
                        disaster_labels.add(mapping['category'])
                        total_weight += mapping['severity_weight']
                        if conf > 0.4 or mapping['is_critical']:
                            is_verified = True
                    else:
                        # General labels for non-disaster specific objects
                        if conf > 0.5:
                            disaster_labels.add(label.capitalize())

            # If nothing specifically disaster-related but high confidence on something
            if not is_verified and max_conf > 0.6:
                is_verified = True

            return {
                "verified": is_verified,
                "confidence": round(max_conf, 2),
                "labels": list(disaster_labels) if disaster_labels else ["General Incident"],
                "severity_boost": round(min(total_weight, 1.5), 2) # Cap the boost
            }

        except Exception as e:
            logger.error(f"SDIRS AI: Error during image analysis: {e}")
            return {"verified": False, "confidence": 0.0, "labels": [f"Error: {str(e)}"], "severity_boost": 0.0}

# Singleton instance for SDIRS
disaster_cv_service = DisasterCVModel()

