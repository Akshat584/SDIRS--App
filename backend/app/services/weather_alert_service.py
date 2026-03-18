import httpx
from typing import Optional
from app.models.weather_alert import WeatherAlertFeed

OPENWEATHERMAP_API_KEY = "YOUR_API_KEY"  # Replace with your OpenWeatherMap API key
OPENWEATHERMAP_API_URL = "https://api.openweathermap.org/data/3.0/onecall"

async def get_weather_alert_data(lat: float, lon: float) -> Optional[WeatherAlertFeed]:
    """
    Fetches weather alert data from the OpenWeatherMap API.
    """
    if OPENWEATHERMAP_API_KEY == "YOUR_API_KEY":
        print("OpenWeatherMap API key not set. Please set it in backend/app/services/weather_alert_service.py")
        return None

    params = {
        "lat": lat,
        "lon": lon,
        "appid": OPENWEATHERMAP_API_KEY,
        "exclude": "current,minutely,hourly,daily"
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(OPENWEATHERMAP_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            # The alerts might not be present in the response if there are no alerts
            if "alerts" not in data:
                data["alerts"] = []
            return WeatherAlertFeed(**data)
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
