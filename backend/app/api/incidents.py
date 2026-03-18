from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
import shutil

from app.db import incidents as db_incidents
from app.db.database import get_db
from app.models import incident as incident_schemas

router = APIRouter()

# Directory to save uploaded photos
UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.get("/incidents", response_model=List[incident_schemas.IncidentOut])
def read_incidents(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """
    Retrieve all incidents from SDIRS.
    """
    incidents = db_incidents.get_all_incidents(db, skip=skip, limit=limit)
    return incidents

@router.post("/incidents", status_code=201)
async def create_incident(
    lat: float = Form(...),
    lon: float = Form(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    incident_type: Optional[str] = Form(None),
    reporter_id: Optional[int] = Form(None),
    photo: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db)
):
    """
    Citizen Reporting API: Receive incident reports with photos, GPS, and descriptions.
    """
    photo_url = None
    if photo:
        # Generate a unique filename to prevent collisions
        file_extension = os.path.splitext(photo.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Save the file locally
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(photo.file, buffer)
        
        # Construct the URL for the photo
        photo_url = f"/static/uploads/{unique_filename}"

    # Prepare the incident creation model
    location = incident_schemas.Location(lat=lat, lon=lon)
    incident_data = incident_schemas.IncidentCreate(
        reporter_id=reporter_id,
        title=title,
        incident_type=incident_type,
        location=location,
        description=description,
        photo_url=photo_url
    )

    # Save to database
    db_incident = await db_incidents.create_incident(db=db, incident=incident_data)
    
    return {
        "status": "success",
        "message": "Incident reported to SDIRS successfully.",
        "incident_id": db_incident.id,
        "photo_url": photo_url
    }
