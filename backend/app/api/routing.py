from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
from app.services.hazard_aware_routing import HazardAwareRoutingService
from app.db.database import get_db

router = APIRouter()

@router.get("/directions", response_model=Dict[str, Any])
async def get_route_directions(
    origin: str = Query(..., description="Starting point (e.g., 'latitude,longitude' or 'address')"),
    destination: str = Query(..., description="Destination point (e.g., 'latitude,longitude' or 'address')"),
    departure_time: str = Query("now", description="The desired time of departure (e.g., 'now' or a timestamp)"),
    db: Session = Depends(get_db)
):
    """
    SDIRS Hazard-Aware Routing (Module 6)
    Get directions and cross-check against live roadblocks/flood reports.
    """
    directions = await HazardAwareRoutingService.get_hazard_safe_route(db, origin, destination, departure_time)
    if directions is None:
        raise HTTPException(status_code=500, detail="Could not fetch hazard-aware directions.")
    return directions

