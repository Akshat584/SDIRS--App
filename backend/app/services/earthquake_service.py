import httpx
from typing import Optional
from app.models.earthquake import EarthquakeFeed

USGS_API_URL = "https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/all_day.geojson"

async def get_earthquake_data() -> Optional[EarthquakeFeed]:
    """
    Fetches earthquake data from the USGS API.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(USGS_API_URL)
            response.raise_for_status()
            data = response.json()
            return EarthquakeFeed(**data)
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
