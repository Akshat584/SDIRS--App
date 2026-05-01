from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.db import schemas as db_models
from pydantic import BaseModel, ConfigDict
from datetime import datetime

router = APIRouter()

class SafetyCheckIn(BaseModel):
    incident_id: Optional[int] = None
    status: str = "safe" # 'safe', 'needs_help'
    message: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class SafetyStatusOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    status: str
    message: Optional[str]
    last_updated: datetime
    user_name: Optional[str] = None

@router.post("/check-in", response_model=SafetyStatusOut)
async def safety_check_in(
    data: SafetyCheckIn,
    current_user_id: int = 1, # Mocked
    db: Session = Depends(get_db)
):
    # Check if existing status exists
    existing = db.query(db_models.SafetyStatus).filter(
        db_models.SafetyStatus.user_id == current_user_id,
        db_models.SafetyStatus.incident_id == data.incident_id
    ).first()

    if existing:
        existing.status = data.status
        existing.message = data.message
        existing.latitude = data.latitude
        existing.longitude = data.longitude
        db.commit()
        db.refresh(existing)
        return existing
    
    new_status = db_models.SafetyStatus(
        user_id=current_user_id,
        incident_id=data.incident_id,
        status=data.status,
        message=data.message,
        latitude=data.latitude,
        longitude=data.longitude
    )
    db.add(new_status)
    db.commit()
    db.refresh(new_status)
    return new_status

@router.get("/status/{user_id_or_email}", response_model=List[SafetyStatusOut])
async def get_user_safety_status(
    user_id_or_email: str,
    db: Session = Depends(get_db)
):
    # Try by ID first
    query = db.query(db_models.SafetyStatus).join(db_models.User)
    
    if user_id_or_email.isdigit():
        results = query.filter(db_models.SafetyStatus.user_id == int(user_id_or_email)).all()
    else:
        results = query.filter(db_models.User.email == user_id_or_email).all()

    # Add user name to output
    for r in results:
        r.user_name = r.user.name
        
    return results
