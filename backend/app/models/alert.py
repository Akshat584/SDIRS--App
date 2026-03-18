from pydantic import BaseModel
from datetime import datetime

class Alert(BaseModel):
    id: int
    message: str
    severity: str
    created_at: datetime
