import os
import httpx
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
GOOGLE_MAPS_DIRECTIONS_API_URL = "https://maps.googleapis.com/maps/api/directions/json"

async def get_directions(origin: str, destination: str, departure_time: str = "now") -> Optional[Dict[str, Any]]:
    """
    Fetches directions from Google Maps Directions API with traffic data.
    """
    if GOOGLE_MAPS_API_KEY == "YOUR_GOOGLE_MAPS_API_KEY" or not GOOGLE_MAPS_API_KEY:
        print("Google Maps API key not set. Please set it in backend/.env")
        return None

    params = {
        "origin": origin,
        "destination": destination,
        "departure_time": departure_time,
        "traffic_model": "best_guess",
        "key": GOOGLE_MAPS_API_KEY
    }
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(GOOGLE_MAPS_DIRECTIONS_API_URL, params=params)
            response.raise_for_status()
            data = response.json()
            if data.get("status") == "OK":
                return data
            else:
                print(f"Google Maps API error: {data.get('error_message', 'Unknown error')}")
                return None
    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
