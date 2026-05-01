from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.db import schemas as db_models
from pydantic import BaseModel, ConfigDict
from datetime import datetime

router = APIRouter()

class MutualAidCreate(BaseModel):
    item_type: str
    description: str
    latitude: float
    longitude: float
    urgency: str = "medium"

class MutualAidOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    user_id: int
    item_type: str
    description: str
    latitude: float
    longitude: float
    status: str
    urgency: str
    created_at: datetime

@router.get("/requests", response_model=List[MutualAidOut])
async def list_mutual_aid_requests(
    item_type: Optional[str] = None,
    status: str = "open",
    db: Session = Depends(get_db)
):
    query = db.query(db_models.MutualAidRequest).filter(db_models.MutualAidRequest.status == status)
    if item_type:
        query = query.filter(db_models.MutualAidRequest.item_type == item_type)
    return query.all()

from app.core.security import get_current_user
from app.models.sqlalchemy import User

@router.post("/requests", response_model=MutualAidOut)
async def create_mutual_aid_request(
    data: MutualAidCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    new_req = db_models.MutualAidRequest(
        user_id=current_user.id,
        item_type=data.item_type,
        description=data.description,
        latitude=data.latitude,
        longitude=data.longitude,
        urgency=data.urgency
    )
    db.add(new_req)
    db.commit()
    db.refresh(new_req)
    return new_req

@router.post("/requests/{request_id}/respond")
async def respond_to_request(
    request_id: int,
    message: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    req = db.query(db_models.MutualAidRequest).filter(db_models.MutualAidRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=404, detail="Request not found")
        
    new_resp = db_models.MutualAidResponse(
        request_id=request_id,
        provider_id=current_user.id,
        message=message,
        status="pending"
    )
    db.add(new_resp)
    db.commit()
    return {"status": "success", "message": "Response sent to neighbor."}
