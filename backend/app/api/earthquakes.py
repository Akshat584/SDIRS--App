from fastapi import APIRouter, HTTPException
from typing import Optional
from app.services import earthquake_service
from app.models.earthquake import EarthquakeFeed

router = APIRouter()

@router.get("/earthquakes", response_model=Optional[EarthquakeFeed])
async def get_earthquakes():
    """
    Get the latest earthquake data from the USGS API.
    """
    earthquakes = await earthquake_service.get_earthquake_data()
    if earthquakes is None:
        raise HTTPException(status_code=500, detail="Could not fetch earthquake data.")
    return earthquakes
