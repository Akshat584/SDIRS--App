import httpx
from typing import Optional
from app.models.earthquake import EarthquakeFeed
from app.services.circuit_breaker import usgs_breaker

USGS_API_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"

async def _fetch_from_usgs() -> EarthquakeFeed:
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(USGS_API_URL)
        response.raise_for_status()
        data = response.json()
        return EarthquakeFeed(**data)

async def get_earthquake_data() -> Optional[EarthquakeFeed]:
    """
    Fetches earthquake data from the USGS API with circuit breaker protection.
    """
    try:
        return await usgs_breaker.call(_fetch_from_usgs)
    except Exception as e:
        print(f"Earthquake Service Error: {e}")
        return None

