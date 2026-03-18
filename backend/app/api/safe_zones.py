from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.services import safe_zone_service
from app.services.safe_zone_service import NearestSafeZoneResult
from typing import Optional

router = APIRouter()

@router.get("/safe-zones/nearest", response_model=Optional[NearestSafeZoneResult])
async def get_nearest_safe_zone(
    origin: str = Query(..., description="Your current location (e.g., 'latitude,longitude' or 'address')"),
    db: Session = Depends(get_db)
):
    """
    Finds the nearest safe zone from a given origin.
    """
    nearest_safe_zone = await safe_zone_service.find_nearest_safe_zone(db, origin)
    if nearest_safe_zone is None:
        raise HTTPException(status_code=404, detail="No safe zones found or could not calculate routes.")
    return nearest_safe_zone
