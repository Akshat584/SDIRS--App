import logging
import asyncio
import os
from typing import Any, Dict, Optional
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models.sqlalchemy import Incident
from app.services.notification_service import notification_service, NotificationService
from app.services.resource_allocation_ai import ResourceAllocationAI
from app.services.image_verification_service import ImageVerificationService
from app.services.prediction_engine import PredictionEngine
from app.services.population_service import population_service
from app.services import severity_service
from app.models import incident as incident_schemas

logger = logging.getLogger("SDIRS_BackgroundTasks")

class BackgroundTaskManager:
    """
    Handles non-critical operations asynchronously to improve API responsiveness.
    """
    
    @staticmethod
    async def process_new_incident(incident_id: int, incident_data: Dict[str, Any]):
        """
        Deep Intelligent Processing: Verification -> Prediction -> Allocation -> Alerting.
        """
        logger.info(f"Background: Starting intelligent processing for incident {incident_id}")
        
        db = SessionLocal()
        try:
            incident = db.query(Incident).filter(Incident.id == incident_id).first()
            if not incident:
                logger.error(f"Background: Incident {incident_id} not found in DB.")
                return

            # 1. AI Image Verification (YOLOv8)
            ai_verified = False
            ai_confidence = 0.0
            if incident.photo_url:
                local_path = incident.photo_url.lstrip("/")
                if os.path.exists(local_path):
                    try:
                        ai_results = await ImageVerificationService.analyze_incident_image(local_path)
                        ai_verified = ai_results.get("verified", False)
                        ai_confidence = ai_results.get("confidence", 0.0)
                        
                        incident.ai_verified = ai_verified
                        incident.ai_confidence = ai_confidence
                        
                        # Auto-assign type if not provided
                        if ai_verified and not incident.incident_type and ai_results.get("labels"):
                            label_map = {"Fire/Smoke": "fire", "Flood/Water": "flood", "Traffic/Accident": "accident"}
                            for label in ai_results["labels"]:
                                if label in label_map:
                                    incident.incident_type = label_map[label]
                                    break
                        
                        if ai_verified:
                            incident.status = "verified"
                    except Exception as e:
                        logger.error(f"Background: CV Verification failed for {incident_id}: {e}")

            # 2. ML Severity Prediction (Random Forest)
            try:
                # Fetch REAL weather data
                weather_data = await PredictionEngine._fetch_weather_data(incident.latitude, incident.longitude)
                temp = weather_data.get("temp", 28.0)
                rainfall = weather_data.get("rainfall", 0.0)
                wind = weather_data.get("wind_speed", 10.0)

                # Fetch REAL population density
                pop_density = await population_service.get_population_density(incident.latitude, incident.longitude)
                
                predicted_sev_enum = severity_service.predict_severity(
                    temp=temp, rainfall=rainfall, wind_speed=wind, 
                    pop_density=pop_density, historical_freq=2.0
                )
                incident.predicted_severity = predicted_sev_enum.value
                incident.weather_snapshot = weather_data
            except Exception as e:
                logger.error(f"Background: Severity prediction failed for {incident_id}: {e}")

            db.commit()

            # 3. Smart Resource AI (V2) Allocation
            try:
                allocated_ids = await ResourceAllocationAI.find_best_resources(db, incident_id)
                if allocated_ids:
                    logger.info(f"Background: AI allocated {len(allocated_ids)} resources to incident {incident_id}")
            except Exception as e:
                logger.error(f"Background: Resource allocation failed for incident {incident_id}: {e}")

            # 4. Automated Omni-Channel Alerting (FCM, Twilio, WebSockets)
            try:
                if incident.ai_verified or incident.predicted_severity in ["high", "critical"]:
                    loc = incident_schemas.Location(lat=incident.latitude, lon=incident.longitude)
                    nearby_data = ResourceAllocationAI.get_nearby_responders(db=db, incident_location=loc, radius_km=10.0)
                    
                    responder_data = [{"id": r.id, "name": r.name, "fcm_token": getattr(r, 'fcm_token', None)} for r in nearby_data["responders"]]
                    resource_data = [{"id": r.id, "name": r.name} for r in nearby_data["resources"]]
                    
                    await NotificationService.trigger_omni_channel_alerts(
                        incident_id=incident_id,
                        nearby_data={
                            "responders": responder_data,
                            "resources": resource_data
                        }
                    )
            except Exception as e:
                logger.error(f"Background: Notification triggering failed for {incident_id}: {e}")

            # 5. Dashboard Broadcast (WebSockets)
            await notification_service.broadcast_incident({
                "id": incident.id,
                "type": incident.incident_type,
                "severity": incident.predicted_severity,
                "lat": incident.latitude,
                "lon": incident.longitude
            })

        except Exception as e:
            logger.error(f"Background: Global error processing incident {incident_id}: {e}")
            db.rollback()
        finally:
            db.close()

    @staticmethod
    async def log_system_event(event_type: str, details: Dict[str, Any]):
        """
        Logs a system event to external monitoring or analytics.
        """
        logger.info(f"Background: System Event - {event_type}")
        # Add logic here
