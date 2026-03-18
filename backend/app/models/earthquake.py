from pydantic import BaseModel
from typing import List, Optional

class EarthquakeProperties(BaseModel):
    mag: float
    place: str
    time: int
    url: str
    tsunami: int
    magType: str
    type: str
    title: str

class Geometry(BaseModel):
    type: str
    coordinates: List[float]

class EarthquakeFeature(BaseModel):
    type: str
    properties: EarthquakeProperties
    geometry: Geometry
    id: str

class EarthquakeFeed(BaseModel):
    type: str
    features: List[EarthquakeFeature]
