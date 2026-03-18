import socketio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SDIRS_WebSockets")

# Initialize Socket.io Async Server
sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')

class SDIRSWebSocketManager:
    """
    SDIRS WebSocket Manager handles real-time coordination between 
    the Citizen App, Responders, and the Emergency Command Center.
    """

    @staticmethod
    @sio.event
    async def connect(sid, environ):
        logger.info(f"SDIRS Client connected: {sid}")
        # In a production scenario, we would verify JWT here via environ['HTTP_AUTHORIZATION']
        await sio.emit('connection_status', {'status': 'connected', 'sid': sid}, to=sid)

    @staticmethod
    @sio.event
    async def disconnect(sid):
        logger.info(f"SDIRS Client disconnected: {sid}")

    @staticmethod
    @sio.event
    async def send_message(sid, data):
        """
        Module 9: Emergency Communication System
        Broadcasts chat messages, commands, or alerts.
        Expected data: {'sender_id': int, 'incident_id': int, 'text': str, 'type': str}
        """
        logger.info(f"Message from {sid}: {data}")
        await sio.emit('receive_message', data)

    @staticmethod
    @sio.event
    async def send_location(sid, data):
        """
        Module 4 & 5: Real-Time Command Center & Resource Allocation
        Updates responder GPS locations on the live map.
        Expected data: {'resource_id': int, 'lat': float, 'lon': float, 'status': str}
        """
        # logger.debug(f"Location Update from {sid}: {data}") # Too noisy for INFO
        await sio.emit('receive_location', data)

    @staticmethod
    @sio.event
    async def incident_update(sid, data):
        """
        Module 3 & 4: Incident Verification & Command Center
        Notifies UI of changes in incident status or severity.
        Expected data: {'incident_id': int, 'status': str, 'severity': str}
        """
        logger.info(f"Incident update: {data}")
        await sio.emit('incident_update', data)

    @staticmethod
    @sio.event
    async def resource_update(sid, data):
        """
        Module 5: Smart Resource Allocation
        Notifies UI of changes in resource availability (e.g., Fire Truck deployed).
        Expected data: {'resource_id': int, 'status': str}
        """
        logger.info(f"Resource update: {data}")
        await sio.emit('resource_update', data)

    @staticmethod
    @sio.event
    async def prediction_alert(sid, data):
        """
        Module 1: Disaster Prediction Engine
        Broadcasts high-risk predictions to the Command Center.
        Expected data: {'type': str, 'location': dict, 'probability': float, 'level': str}
        """
        logger.info(f"Prediction Alert: {data}")
        await sio.emit('prediction_alert', data)

# Export the sio instance to be mounted in main.py
def get_sio_server():
    return sio
