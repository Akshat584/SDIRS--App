from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class DroneTelemetry(BaseModel):
    drone_id: str
    lat: float
    lon: float
    altitude: float
    speed: float
    battery_percentage: int
    status: str # 'idle', 'en_route', 'scanning', 'returning', 'searching'
    last_update: datetime
    search_area: Optional[List[float]] = None # [min_lat, min_lon, max_lat, max_lon]
    detections: Optional[List[dict]] = [] # [{"type": "human", "confidence": 0.98, "lat": 26.85, "lon": 80.95}]

class DroneFeed(BaseModel):
    drone_id: str
    stream_url: str # Placeholder URL for the video stream
    is_active: bool
    incident_id: Optional[int] = None

class DroneResponse(BaseModel):
    drones: List[DroneTelemetry]
    timestamp: datetime
