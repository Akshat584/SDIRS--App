from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from app.services import weather_alert_service
from app.models.weather_alert import WeatherAlertFeed

router = APIRouter()

@router.get("/weather-alerts", response_model=Optional[WeatherAlertFeed])
async def get_weather_alerts(
    lat: float = Query(..., description="Latitude"),
    lon: float = Query(..., description="Longitude")
):
    """
    Get the latest weather alert data from the OpenWeatherMap API.
    """
    weather_alerts = await weather_alert_service.get_weather_alert_data(lat, lon)
    if weather_alerts is None:
        raise HTTPException(status_code=500, detail="Could not fetch weather alert data.")
    return weather_alerts
