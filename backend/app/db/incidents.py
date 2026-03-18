from sqlalchemy.orm import Session
from geoalchemy2.shape import to_shape
from geoalchemy2.elements import WKTElement
import asyncio

from app.db import schemas as db_models
from app.models import incident as incident_schemas
from app.services.severity_service import predict_severity, predict_resource_demand, Severity
from app.services.image_verification_service import ImageVerificationService
from app.services.resource_allocation_ai import ResourceAllocationAI
from app.services.notification_service import NotificationService

def get_all_incidents(db: Session, skip: int = 0, limit: int = 100):
    """
    Retrieve all incidents from the database.
    """
    incidents = db.query(db_models.Incident).order_by(db_models.Incident.reported_at.desc()).offset(skip).limit(limit).all()
    
    results = []
    for incident in incidents:
        # Convert the WKBElement to a shapely Point
        point = to_shape(incident.location)
        location_dict = incident_schemas.Location(lat=point.y, lon=point.x)
        
        # Create the output model
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
    Create a new incident in the database with AI-powered severity and SDIRS verification.
    """
    # Create a WKT string from the location data
    point_wkt = f'POINT({incident.location.lon} {incident.location.lat})'
    
    # 1. INITIAL AI PREDICTION (Module 1)
    temp = 30.0
    rainfall = 50.0
    wind_speed = 15.0
    pop_density = 1000.0
    historical_freq = 2.0
    severity = predict_severity(temp, rainfall, wind_speed, pop_density, historical_freq)
    
    # 2. SDIRS AI INCIDENT VERIFICATION (Module 3)
    ai_verified = False
    ai_confidence = 0.0
    if incident.photo_url:
        # Strip leading slash if present to get relative path
        img_path = incident.photo_url.lstrip('/')
        analysis = await ImageVerificationService.analyze_incident_image(img_path)
        ai_verified = analysis["verified"]
        ai_confidence = analysis["confidence"]

    # Create the SQLAlchemy model instance
    db_incident = db_models.Incident(
        reporter_id=incident.reporter_id,
        title=incident.title,
        incident_type=incident.incident_type,
        location=WKTElement(point_wkt, srid=4326),
        description=incident.description,
        photo_url=incident.photo_url,
        
        # AI Intelligence Fields (Module 3)
        ai_verified=ai_verified,
        ai_confidence=ai_confidence,
        predicted_severity=severity.value,
        
        status='verified' if ai_verified else 'pending'
    )
    
    db.add(db_incident)
    db.commit()
    db.refresh(db_incident)

    # 3. SMART RESOURCE ALLOCATION AI (Module 5)
    # If incident is verified, trigger automatic resource allocation
    if db_incident.ai_verified:
        # Spatial Alert: Find all responders/ambulances within 5km (ST_DWithin)
        nearby = ResourceAllocationAI.get_nearby_responders(db, db_incident.location, radius_km=5.0)
        
        # OMNI-CHANNEL TRIGGER (Module 9)
        # Broadcast to WebSockets, FCM, and Twilio
        await NotificationService.trigger_omni_channel_alerts(db_incident.id, nearby)

        allocated_ids = await ResourceAllocationAI.find_best_resources(db, db_incident.id)
        if allocated_ids:
            db_incident.status = 'dispatched'
            db.commit()

    return db_incident
