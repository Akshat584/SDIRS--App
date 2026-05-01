from pydantic import BaseModel, field_validator, ConfigDict
from typing import Optional, Any, List
from datetime import datetime

# Pydantic model for location data
class Location(BaseModel):
    lat: float
    lon: float

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

# Pydantic model for creating a new incident (Internal)
class IncidentCreate(BaseModel):
    reporter_id: Optional[int] = None
    title: Optional[str] = None
    incident_type: Optional[str] = None
    location: Location
    description: Optional[str] = None
    photo_url: Optional[str] = None

# Pydantic model for representing an incident in API responses
class IncidentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    reporter_id: Optional[int] = None
    title: Optional[str] = None
    incident_type: Optional[str] = None
    location: Location
    description: Optional[str] = None
    photo_url: Optional[str] = None
    
    ai_verified: bool
    ai_confidence: Optional[float] = None
    predicted_severity: Optional[str] = None
    status: str
    
    reported_at: datetime
    resolved_at: Optional[datetime] = None

class IncidentAnalysisRequest(BaseModel):
    description: str
    image_uri: Optional[str] = None
    latitude: float = 0.0
    longitude: float = 0.0

class IncidentAnalysisResponse(BaseModel):
    severity: str
    verified: bool
    ml_labels: List[str]
