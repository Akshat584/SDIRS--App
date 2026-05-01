import logging
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional
import math

from app.db import schemas as db_models
from app.services import google_maps_service
from app.utils.geo import haversine, is_within_radius

logger = logging.getLogger("SDIRS_Hazard_Routing")

class HazardAwareRoutingService:
    """
    SDIRS Hazard-Aware Routing (Module 6)
    Integrates live road closures and flood reports into the navigation algorithm.
    """

    @staticmethod
    async def get_hazard_safe_route(db: Session, origin: str, destination: str, departure_time: str = "now") -> Dict[str, Any]:
        """
        Gets directions from Google Maps and cross-checks with active SDIRS hazards.
        """
        # 1. Get standard traffic-aware route from Google Maps
        directions = await google_maps_service.get_directions(origin, destination, departure_time)
        
        if not directions or directions.get("status") != "OK":
            return directions

        # 2. Fetch active SDIRS hazards (Roadblocks, Floods) from DB
        hazards = db.query(db_models.Incident).filter(
            db_models.Incident.incident_type.in_(["flood", "roadblock", "fire"]),
            db_models.Incident.status.in_(["verified", "active", "dispatched"])
        ).all()

        if not hazards:
            return directions

        # 3. Cross-check route legs/steps against hazard locations
        route = directions["routes"][0]
        legs = route["legs"]
        
        hazards_found = []
        for hazard in hazards:
            # Cross-check using latitude and longitude fields
            h_lat, h_lon = hazard.latitude, hazard.longitude
            
            # Check if any part of the route is near the hazard (within 200m)
            is_near, min_dist = HazardAwareRoutingService._is_route_near_point(legs, h_lat, h_lon, 0.2)
            
            if is_near:
                hazards_found.append({
                    "id": hazard.id,
                    "type": hazard.incident_type,
                    "severity": hazard.predicted_severity,
                    "distance_meters": round(min_dist * 1000, 1),
                    "location": {"lat": h_lat, "lon": h_lon}
                })

        # 4. Inject hazard alerts into the response
        directions["sdirs_hazards"] = hazards_found
        if hazards_found:
            directions["hazard_warning"] = f"CRITICAL: {len(hazards_found)} active hazards detected along this route. Exercise extreme caution."
            logger.warning(f"SDIRS Hazard Routing: Found {len(hazards_found)} hazards for route from {origin} to {destination}.")
        
        return directions

    @staticmethod
    def _is_route_near_point(legs: List[Any], p_lat: float, p_lon: float, radius_km: float) -> tuple:
        """
        Check if any step in the route legs is within radius_km of a point.
        """
        min_dist = float('inf')
        found = False
        
        for leg in legs:
            for step in leg["steps"]:
                # Check start and end of each step
                s_lat = step["start_location"]["lat"]
                s_lon = step["start_location"]["lng"]
                e_lat = step["end_location"]["lat"]
                e_lon = step["end_location"]["lng"]
                
                d1 = haversine(s_lat, s_lon, p_lat, p_lon)
                d2 = haversine(e_lat, e_lon, p_lat, p_lon)
                
                step_min = min(d1, d2)
                if step_min < min_dist:
                    min_dist = step_min
                
                if step_min <= radius_km:
                    found = True
        
        return found, min_dist

