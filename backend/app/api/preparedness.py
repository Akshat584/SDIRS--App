from fastapi import APIRouter
from app.services.preparedness_service import PreparednessService

router = APIRouter()

@router.get("/manual/{threat_type}")
async def get_preparedness_manual(threat_type: str):
    """
    Get the preparedness checklist and first aid manual for a specific threat.
    """
    return PreparednessService.get_manual(threat_type)
