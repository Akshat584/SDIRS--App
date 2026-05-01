from pydantic import BaseModel, field_validator
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

    @field_validator('lat')
    @classmethod
    def validate_latitude(cls, v):
        if not -90 <= v <= 90:
            raise ValueError('Latitude must be between -90 and 90 degrees')
        return v

    @field_validator('lon')
    @classmethod
    def validate_longitude(cls, v):
        if not -180 <= v <= 180:
            raise ValueError('Longitude must be between -180 and 180 degrees')
        return v

class DroneFeed(BaseModel):
    drone_id: str
    stream_url: str # Placeholder URL for the video stream
    is_active: bool
    incident_id: Optional[int] = None

class DroneResponse(BaseModel):
    drones: List[DroneTelemetry]
    timestamp: datetime
