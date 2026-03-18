from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.db import schemas as db_models
from app.models.message import MessageCreate, MessageOut

router = APIRouter()

@router.get("/messages", response_model=List[MessageOut])
async def get_messages(
    incident_id: Optional[int] = Query(None, description="Filter messages by incident ID"),
    message_type: Optional[str] = Query(None, description="Filter by message type ('chat', 'broadcast', 'command')"),
    limit: int = Query(50, le=100),
    db: Session = Depends(get_db)
):
    """
    SDIRS Module 9: Retrieve historical messages for an incident or system-wide broadcasts.
    """
    query = db.query(db_models.Message)
    
    if incident_id:
        query = query.filter(db_models.Message.incident_id == incident_id)
    if message_type:
        query = query.filter(db_models.Message.message_type == message_type)
        
    messages = query.order_by(db_models.Message.sent_at.desc()).limit(limit).all()
    return messages

@router.post("/messages", response_model=MessageOut)
async def create_message(message: MessageCreate, db: Session = Depends(get_db)):
    """
    Store a new message in the database (Module 9).
    This can be used to archive messages sent via WebSockets.
    """
    db_message = db_models.Message(
        incident_id=message.incident_id,
        sender_id=message.sender_id,
        message_text=message.message_text,
        message_type=message.message_type
    )
    db.add(db_message)
    db.commit()
    db.refresh(db_message)
    return db_message
