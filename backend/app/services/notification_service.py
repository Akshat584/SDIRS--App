import logging
import os
import firebase_admin
from firebase_admin import credentials, messaging
from twilio.rest import Client as TwilioClient
from app.core.websockets import get_sio_server
from app.core.config import settings
from typing import List, Dict, Optional

logger = logging.getLogger("SDIRS_Notification")
sio = get_sio_server()

# Initialize Firebase Admin SDK
try:
    if settings.firebase_service_account_path and os.path.exists(settings.firebase_service_account_path):
        cred = credentials.Certificate(settings.firebase_service_account_path)
        firebase_admin.initialize_app(cred)
        logger.info("Firebase Admin initialized successfully.")
    else:
        logger.warning("Firebase service account path not provided or file not found. Push notifications will be mocked.")
except Exception as e:
    logger.error(f"Failed to initialize Firebase: {e}")

class NotificationService:
    """
    SDIRS Omni-Channel Notification Service
    Handles real-time alerts across WebSockets, FCM, and SMS.
    """

    @staticmethod
    async def trigger_omni_channel_alerts(incident_id: int, nearby_data: Dict):
        """
        Triggers alerts across all supported channels for an incident.
        """
        resources = nearby_data.get("resources", [])
        responders = nearby_data.get("responders", [])

        # 1. WebSocket Broadcast to Responder Dashboards
        await NotificationService.broadcast_to_dashboards(incident_id, resources, responders)

        # 2. FCM Push Notifications for Mobile Devices
        if responders:
            await NotificationService.send_fcm_notifications(incident_id, responders)

        # 3. SMS/Voice Alerts for Senior Officials (Authorities)
        await NotificationService.send_authority_alerts(incident_id)

    @staticmethod
    async def broadcast_to_dashboards(incident_id: int, resources: List, responders: List):
        """
        Real-time WebSocket broadcast to active responder dashboards.
        """
        data = {
            "incident_id": incident_id,
            "message": f"EMERGENCY: New verified incident {incident_id} detected nearby!",
            "nearby_ambulances": len(resources),
            "nearby_responders": len(responders),
            "type": "SPATIAL_ALERT"
        }
        
        await sio.emit('spatial_alert', data)
        logger.info(f"WebSocket: Broadcasted spatial alert for incident {incident_id} to dashboards.")

    @staticmethod
    async def send_fcm_notifications(incident_id: int, responders: List):
        """
        Firebase Cloud Messaging (FCM) push notifications for mobile devices.
        """
        if not firebase_admin._apps:
            logger.info(f"FCM (Mock): Sending push notifications to {len(responders)} nearby responders for incident {incident_id}.")
            return

        # Assuming responders list contains dictionaries with 'fcm_token'
        tokens = [r.get("fcm_token") for r in responders if r.get("fcm_token")]
        
        if not tokens:
            return

        message = messaging.MulticastMessage(
            notification=messaging.Notification(
                title="🚨 DISASTER ALERT",
                body=f"New incident detected near your location. Responder action required.",
            ),
            data={"incident_id": str(incident_id), "type": "DISASTER_ALERT"},
            tokens=tokens,
        )

        try:
            response = messaging.send_multicast(message)
            logger.info(f"FCM: Successfully sent {response.success_count} notifications for incident {incident_id}.")
        except Exception as e:
            logger.error(f"FCM Error: Failed to send notifications: {e}")

    @staticmethod
    async def send_authority_alerts(incident_id: int):
        """
        SMS/Voice alerts via Twilio API for senior officials.
        """
        if not all([settings.twilio_account_sid, settings.twilio_auth_token, settings.twilio_from_number]):
            logger.info(f"Twilio (Mock): Sending SMS/Voice alerts to senior officials for incident {incident_id}.")
            return

        try:
            client = TwilioClient(settings.twilio_account_sid, settings.twilio_auth_token)
            # In a real scenario, fetch official numbers from DB
            official_numbers = ["+1234567890"] 
            
            for number in official_numbers:
                client.messages.create(
                    body=f"SDIRS PRIORITY 1: New verified incident {incident_id} reported. Immediate oversight required.",
                    from_=settings.twilio_from_number,
                    to=number
                )
            logger.info(f"Twilio: Successfully sent alerts to {len(official_numbers)} officials.")
        except Exception as e:
            logger.error(f"Twilio Error: {e}")

# Instantiate the service for use across SDIRS
notification_service = NotificationService()

