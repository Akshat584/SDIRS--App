from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class HeatmapPoint(BaseModel):
    lat: float
    lon: float
    intensity: float  # 0.0 to 1.0
    type: str         # 'incident', 'prediction', 'hazard'
    label: str        # e.g., 'Fire', 'Flood Risk'
    radius: Optional[int] = 500 # radius in meters for the risk zone

class HeatmapResponse(BaseModel):
    points: List[HeatmapPoint]
    timestamp: datetime
