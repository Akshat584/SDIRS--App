from pydantic import BaseModel
from typing import List, Optional

class WeatherAlert(BaseModel):
    sender_name: str
    event: str
    start: int
    end: int
    description: str

class WeatherAlertFeed(BaseModel):
    lat: float
    lon: float
    alerts: List[WeatherAlert]
