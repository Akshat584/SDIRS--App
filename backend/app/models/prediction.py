from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class DisasterRisk(BaseModel):
    disaster_type: str
    probability: float
    alert_level: str
    area: str
    recommendations: List[str]

class PredictionResponse(BaseModel):
    location: dict
    timestamp: datetime
    risks: List[DisasterRisk]
