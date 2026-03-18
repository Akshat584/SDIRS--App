import logging
from app.core.websockets import get_sio_server
from typing import List, Dict

logger = logging.getLogger("SDIRS_Notification")
sio = get_sio_server()

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

        if not resources and not responders:
            return

        # 1. WebSocket Broadcast to Responder Dashboards
        await NotificationService.broadcast_to_dashboards(incident_id, resources, responders)

        # 2. FCM Push Notifications for Mobile Devices
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
        
        # Broadcast to all connected clients (in production, we'd target responder rooms)
        await sio.emit('spatial_alert', data)
        logger.info(f"WebSocket: Broadcasted spatial alert for incident {incident_id} to dashboards.")

    @staticmethod
    async def send_fcm_notifications(incident_id: int, responders: List):
        """
        Firebase Cloud Messaging (FCM) push notifications for mobile devices.
        Note: Requires 'firebase-admin' package and service account.
        """
        # Placeholder for FCM logic
        # In real SDIRS: [messaging.Message(notification=..., token=r.fcm_token) for r in responders]
        logger.info(f"FCM: Sending push notifications to {len(responders)} nearby responders for incident {incident_id}.")
        # Mocking successful send
        pass

    @staticmethod
    async def send_authority_alerts(incident_id: int):
        """
        SMS/Voice alerts via Twilio API for senior officials (Authority API).
        Note: Requires 'twilio' package and credentials.
        """
        # Placeholder for Twilio logic
        # In real SDIRS: client.messages.create(body=msg, from_=TWILIO_NUM, to=OFFICIAL_NUM)
        logger.info(f"Twilio: Sending SMS/Voice alerts to senior officials for incident {incident_id}.")
        # Mocking successful send
        pass
