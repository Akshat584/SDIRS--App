from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import uuid
import shutil
from PIL import Image
import io
from pydantic import ValidationError
from app.core.config import settings
from app.services.background_tasks import BackgroundTaskManager
from app.core.limiter import limiter
from fastapi import Request

from app.db import incidents as db_incidents
from app.db.database import get_db
from app.models import incident as incident_schemas
from app.core.security import RoleChecker, get_current_user
from app.models.sqlalchemy import User

router = APIRouter()

# Role checkers
admin_or_responder = RoleChecker(["admin", "responder"])

# Directory to save uploaded photos from settings
UPLOAD_DIR = settings.upload_dir
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif'}

def sanitize_filename(filename: str) -> str:
    """
    Sanitizes a filename to prevent directory traversal.
    """
    return os.path.basename(filename).replace(" ", "_").replace("..", "")

async def validate_image_upload(file: UploadFile):
    """
    Validates an uploaded image file for size, extension, and content.
    Returns the file contents if valid.
    """
    # 1. Check extension
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File extension {file_extension} not allowed. Only {ALLOWED_EXTENSIONS} are supported."
        )

    # 2. Check size (read into memory to check size)
    contents = await file.read()
    if len(contents) > settings.max_file_size:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds the maximum limit of {settings.max_file_size / (1024*1024)}MB."
        )
    
    # 3. Verify it's actually an image using Pillow (Python 3.14 compatible)
    try:
        img = Image.open(io.BytesIO(contents))
        img.verify() # Verify it's a valid image
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid image file content. The file is not a valid image."
        )
    
    return contents

@router.get("/incidents", response_model=List[incident_schemas.IncidentOut])
def read_incidents(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    current_user = Depends(admin_or_responder)
):
    """
    Retrieve all incidents from SDIRS. (Admin/Responder only)
    """
    incidents = db_incidents.get_all_incidents(db, skip=skip, limit=limit)
    return incidents

@router.post("/incidents", status_code=201)
@limiter.limit("2/minute")
async def create_incident(
    request: Request,
    background_tasks: BackgroundTasks,
    lat: float = Form(...),
    lon: float = Form(...),
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    incident_type: Optional[str] = Form(None),
    photo: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Citizen Reporting API: Receive incident reports with photos, GPS, and descriptions.
    """
    # Validate coordinates
    try:
        location_data = incident_schemas.Location(lat=lat, lon=lon)
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))

    photo_url = None
    if photo:
        # Validate the photo (size, extension, content)
        contents = await validate_image_upload(photo)

        # Generate a unique filename to prevent collisions
        file_extension = os.path.splitext(photo.filename)[1].lower()
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # Save the file locally using the validated contents
        with open(file_path, "wb") as buffer:
            buffer.write(contents)
        
        # Construct the URL for the photo
        photo_url = f"/static/uploads/{unique_filename}"

    # Prepare the incident creation model
    incident_data = incident_schemas.IncidentCreate(
        reporter_id=current_user.id,
        title=title,
        incident_type=incident_type,
        location=location_data,
        description=description,
        photo_url=photo_url
    )

    # Save to database
    db_incident = await db_incidents.create_incident(db=db, incident=incident_data)
    
    # Offload non-critical tasks to background
    background_tasks.add_task(
        BackgroundTaskManager.process_new_incident, 
        db_incident.id, 
        {"type": incident_type, "severity": db_incident.predicted_severity}
    )
    
    return {
        "status": "success",
        "message": "Incident reported to SDIRS successfully.",
        "incident_id": db_incident.id,
        "photo_url": photo_url
    }
