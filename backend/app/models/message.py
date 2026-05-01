from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class MessageCreate(BaseModel):
    incident_id: Optional[int] = None
    sender_id: int
    message_text: str
    message_type: str = "chat" # 'chat', 'broadcast', 'command'

class MessageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    incident_id: Optional[int]
    sender_id: int
    message_text: str
    message_type: str
    sent_at: datetime
