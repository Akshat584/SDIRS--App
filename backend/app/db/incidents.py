from sqlalchemy.orm import Session
from app.models.sqlalchemy import Incident as DbIncident, User
from app.models import incident as incident_schemas
from app.services.image_verification_service import ImageVerificationService
from app.services.notification_service import NotificationService
from app.services.prediction_engine import PredictionEngine
from app.services.population_service import population_service
from app.services import severity_service
import os

def get_all_incidents(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieve all incidents from the database.
    """
    incidents = db.query(DbIncident).order_by(DbIncident.reported_at.desc()).offset(skip).limit(limit).all()

    results = []
    for incident in incidents:
        location_dict = incident_schemas.Location(lat=incident.latitude, lon=incident.longitude)

        incident_out = incident_schemas.IncidentOut(
            id=incident.id,
            reporter_id=incident.reporter_id,
            title=incident.title,
            incident_type=incident.incident_type,
            location=location_dict,
            description=incident.description,
            photo_url=incident.photo_url,
            ai_verified=incident.ai_verified or False,
            ai_confidence=incident.ai_confidence,
            predicted_severity=incident.predicted_severity,
            status=incident.status,
            reported_at=incident.reported_at,
            resolved_at=incident.resolved_at
        )
        results.append(incident_out)

    return results


async def create_incident(db: Session, incident: incident_schemas.IncidentCreate):
    """
    SDIRS Optimized Incident Creation.
    API returns immediately after saving core data. AI processing is handled in background.
    """
    lat = incident.location.lat
    lon = incident.location.lon

    db_incident = DbIncident(
        reporter_id=incident.reporter_id,
        title=incident.title,
        incident_type=incident.incident_type,
        latitude=lat,
        longitude=lon,
        description=incident.description,
        photo_url=incident.photo_url,
        ai_verified=False,
        ai_confidence=0.0,
        predicted_severity="low", # Default until AI processes
        status='pending'
    )

    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)

    return db_incident
