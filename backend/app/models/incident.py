from pydantic import BaseModel
from typing import Optional, Any, List
from datetime import datetime

# Pydantic model for location data
class Location(BaseModel):
    lat: float
    lon: float

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

    class Config:
        from_attributes = True

class IncidentAnalysisRequest(BaseModel):
    description: str
    image_uri: Optional[str] = None

class IncidentAnalysisResponse(BaseModel):
    severity: str
    verified: bool
    ml_labels: List[str]
