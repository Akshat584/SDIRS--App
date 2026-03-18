from sqlalchemy.orm import Session
from app.db import schemas
from typing import List

def get_safe_zones(db: Session) -> List[schemas.SafeZone]:
    return db.query(schemas.SafeZone).all()
