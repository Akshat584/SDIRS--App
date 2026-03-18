from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class User(BaseModel):
    id: int
    phone_number: str
    email: Optional[str] = None
    created_at: datetime

class DisasterEvent(BaseModel):
    id: int
    disaster_type: str
    latitude: float
    longitude: float
    severity: Optional[str] = None
    timestamp: datetime
    verified: bool
    source: Optional[str] = None
    created_at: datetime

class EarthquakeDetails(BaseModel):
    event_id: int
    magnitude: Optional[float] = None
    depth: Optional[float] = None
    tsunami_warning: Optional[bool] = None

class FloodDetails(BaseModel):
    event_id: int
    water_level: Optional[float] = None
    precipitation_rate: Optional[float] = None

class WildfireDetails(BaseModel):
    event_id: int
    fire_front_distance: Optional[float] = None
    wind_speed: Optional[float] = None
    wind_direction: Optional[str] = None

class Incident(BaseModel):
    id: int
    user_id: int
    latitude: float
    longitude: float
    description: Optional[str] = None
    photo_url: Optional[str] = None
    timestamp: datetime

class Alert(BaseModel):
    id: int
    event_id: int
    user_id: int
    message: str
    sent_at: datetime
    channel: str

class SafeZone(BaseModel):
    id: int
    name: str
    latitude: float
    longitude: float
    capacity: Optional[int] = None
    created_at: datetime

class Resource(BaseModel):
    id: int
    name: str
    resource_type: Optional[str] = None
    latitude: float
    longitude: float
    availability: Optional[int] = None
    last_updated: Optional[datetime] = None

class CrowdsourcedReport(BaseModel):
    id: int
    user_id: int
    report_type: str
    latitude: float
    longitude: float
    description: Optional[str] = None
    verified: bool
    timestamp: datetime

class Token(BaseModel):
    access_token: str
    token_type: str
