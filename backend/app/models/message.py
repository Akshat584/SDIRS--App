from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class MessageCreate(BaseModel):
    incident_id: Optional[int] = None
    sender_id: int
    message_text: str
    message_type: str = "chat" # 'chat', 'broadcast', 'command'

class MessageOut(BaseModel):
    id: int
    incident_id: Optional[int]
    sender_id: int
    message_text: str
    message_type: str
    sent_at: datetime

    class Config:
        from_attributes = True
