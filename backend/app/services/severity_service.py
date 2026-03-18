from enum import Enum
from typing import Optional, List, Dict
import joblib
import os
import numpy as np

class Severity(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# Load models
MODEL_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'ml_pipeline', 'models')
severity_model_path = os.path.join(MODEL_DIR, 'severity_model.joblib')
resource_model_path = os.path.join(MODEL_DIR, 'resource_model.joblib')

severity_model = joblib.load(severity_model_path) if os.path.exists(severity_model_path) else None
resource_model = joblib.load(resource_model_path) if os.path.exists(resource_model_path) else None

SEVERITY_MAPPING = {
    0: Severity.LOW,
    1: Severity.MEDIUM,
    2: Severity.HIGH,
    3: Severity.CRITICAL
}

def predict_severity(temp: float, rainfall: float, wind_speed: float, pop_density: float, historical_freq: float) -> Severity:
    """
    Predicts incident severity using the Random Forest Classifier.
    """
    if severity_model:
        features = np.array([[temp, rainfall, wind_speed, pop_density, historical_freq]])
        prediction = severity_model.predict(features)[0]
        return SEVERITY_MAPPING.get(prediction, Severity.LOW)
    return Severity.LOW

def predict_resource_demand(severity: Severity, pop_density: float, weather_intensity: float) -> Dict[str, int]:
    """
    Predicts required resources using the Random Forest Regressor.
    """
    if resource_model:
        severity_value = list(SEVERITY_MAPPING.keys())[list(SEVERITY_MAPPING.values()).index(severity)]
        features = np.array([[severity_value, pop_density, weather_intensity]])
        prediction = resource_model.predict(features)[0]
        return {
            "ambulances": int(round(prediction[0])),
            "fire_trucks": int(round(prediction[1])),
            "rescue_boats": int(round(prediction[2]))
        }
    return {"ambulances": 0, "fire_trucks": 0, "rescue_boats": 0}

def get_earthquake_severity(magnitude: float) -> Severity:
    if magnitude >= 7.0:
        return Severity.CRITICAL
    elif magnitude >= 5.0:
        return Severity.HIGH
    elif magnitude >= 3.0:
        return Severity.MEDIUM
    else:
        return Severity.LOW

def get_overall_severity(
    earthquake_magnitude: Optional[float] = None,
    flood_event_type: Optional[str] = None,
    wildfire_event_type: Optional[str] = None
) -> Severity:
    # Keeps legacy support for simple rule-based checks
    severities = []
    if earthquake_magnitude is not None:
        severities.append(get_earthquake_severity(earthquake_magnitude))
    
    if Severity.CRITICAL in severities:
        return Severity.CRITICAL
    elif Severity.HIGH in severities:
        return Severity.HIGH
    elif Severity.MEDIUM in severities:
        return Severity.MEDIUM
    else:
        return Severity.LOW
