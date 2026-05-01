import httpx
from typing import Optional
from app.models.weather_alert import WeatherAlertFeed
from app.services.circuit_breaker import weather_breaker

from app.core.config import settings

OPENWEATHERMAP_API_URL = "https://api.openweathermap.org/data/3.0/onecall"

async def _fetch_from_openweathermap(lat: float, lon: float) -> WeatherAlertFeed:
    params = {
        "lat": lat,
        "lon": lon,
        "appid": settings.openweathermap_api_key,
        "exclude": "current,minutely,hourly,daily"
    }
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(OPENWEATHERMAP_API_URL, params=params)
        response.raise_for_status()
        data = response.json()
        if "alerts" not in data:
            data["alerts"] = []
        return WeatherAlertFeed(**data)

async def get_weather_alert_data(lat: float, lon: float) -> Optional[WeatherAlertFeed]:
    """
    Fetches weather alert data from the OpenWeatherMap API with circuit breaker protection.
    """
    if not settings.openweathermap_api_key or settings.openweathermap_api_key == "YOUR_API_KEY":
        print("OpenWeatherMap API key not set. Please set it in backend/.env")
        return None

    try:
        return await weather_breaker.call(_fetch_from_openweathermap, lat, lon)
    except Exception as e:
        print(f"Weather Alert Service Error: {e}")
        return None

