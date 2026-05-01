from sqlalchemy.orm import Session
from app.db import safe_zones as db_safe_zones
from app.services.google_maps_service import get_directions, get_distance_matrix
from app.utils.geo import haversine
from pydantic import BaseModel, ConfigDict
from typing import List, Dict, Any, Optional

class NearestSafeZoneResult(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    safe_zone_id: int
    safe_zone_name: str
    distance_text: str
    duration_text: str
    route_url: str


async def find_nearest_safe_zone(db: Session, origin: str) -> Optional[NearestSafeZoneResult]:
    """
    Finds the nearest safe zone from a given origin based on travel duration.
    Uses batch Distance Matrix API for efficiency.
    """
    safe_zones = db_safe_zones.get_safe_zones(db)
    
    if not safe_zones:
        return None

    # Try to parse origin lat/lon for pre-filtering
    origin_coords = None
    try:
        if "," in origin:
            olat, olon = map(float, origin.split(","))
            origin_coords = (olat, olon)
    except:
        pass

    # Pre-filter: keep only zones within 50km if possible to stay within API limits
    candidates = []
    for sz in safe_zones:
        if origin_coords:
            dist_km = haversine(origin_coords[0], origin_coords[1], sz.latitude, sz.longitude)
            if dist_km <= 50:
                candidates.append(sz)
    
    # Fallback if no zones within 50km
    if not candidates:
        candidates = safe_zones[:10] # Limit to top 10 for performance

    destinations = "|".join([f"{sz.latitude},{sz.longitude}" for sz in candidates])
    matrix_data = await get_distance_matrix(origin, destinations)

    if not matrix_data or "rows" not in matrix_data or not matrix_data["rows"]:
        return None

    results = matrix_data["rows"][0]["elements"]
    
    nearest_sz = None
    min_duration = float('inf')

    for i, res in enumerate(results):
        if res["status"] == "OK":
            duration_val = res["duration"]["value"]
            if duration_val < min_duration:
                min_duration = duration_val
                sz = candidates[i]
                nearest_sz = NearestSafeZoneResult(
                    safe_zone_id=sz.id,
                    safe_zone_name=sz.name,
                    distance_text=res["distance"]["text"],
                    duration_text=res["duration"]["text"],
                    route_url=f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={sz.latitude},{sz.longitude}"
                )

    return nearest_sz
