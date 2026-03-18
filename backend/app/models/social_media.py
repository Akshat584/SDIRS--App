from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Tweet(BaseModel):
    url: str
    date: datetime
    content: str
    username: str
    sentiment: Optional[float] = 0.0 # -1.0 to 1.0
    classification: Optional[str] = "chatter" # alert, report, request, chatter
