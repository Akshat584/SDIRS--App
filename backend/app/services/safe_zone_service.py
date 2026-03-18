from sqlalchemy.orm import Session
from geoalchemy2.shape import to_shape
from app.db import safe_zones as db_safe_zones
from app.services.google_maps_service import get_directions
from typing import List, Dict, Any, Optional

class NearestSafeZoneResult:
    def __init__(self, safe_zone_id: int, safe_zone_name: str, distance_text: str, duration_text: str, route_url: str):
        self.safe_zone_id = safe_zone_id
        self.safe_zone_name = safe_zone_name
        self.distance_text = distance_text
        self.duration_text = duration_text
        self.route_url = route_url

async def find_nearest_safe_zone(db: Session, origin: str) -> Optional[NearestSafeZoneResult]:
    """
    Finds the nearest safe zone from a given origin based on travel duration.
    """
    safe_zones = db_safe_zones.get_safe_zones(db)
    
    if not safe_zones:
        return None

    nearest_safe_zone = None
    min_duration_seconds = float('inf')

    for sz in safe_zones:
        # Convert the WKBElement to a shapely Point to get lat/lon
        point = to_shape(sz.location)
        sz_lat, sz_lon = point.y, point.x
        
        destination = f"{sz_lat},{sz_lon}"
        directions = await get_directions(origin, destination)
        
        if directions and directions["routes"]:
            # Assuming the first route is the best one
            route = directions["routes"][0]
            leg = route["legs"][0] # Assuming one leg for origin to destination
            
            duration_seconds = leg["duration"]["value"]
            
            if duration_seconds < min_duration_seconds:
                min_duration_seconds = duration_seconds
                nearest_safe_zone = NearestSafeZoneResult(
                    safe_zone_id=sz.id,
                    safe_zone_name=sz.name,
                    distance_text=leg["distance"]["text"],
                    duration_text=leg["duration"]["text"],
                    route_url=f"https://www.google.com/maps/dir/?api=1&origin={origin}&destination={destination}"
                )
    return nearest_safe_zone
