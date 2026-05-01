import socketio
import structlog
from app.db.database import SessionLocal
from app.db.schemas import Message, SOSAlert
import app.db.schemas as db_models
from sqlalchemy.orm import Session

from datetime import datetime
from app.core.config import settings
from app.core.security import decode_access_token
from urllib.parse import parse_qs

# Configure logging
logger = structlog.get_logger("SDIRS_WebSockets")

# Initialize Socket.io Async Server with proper CORS
sio = socketio.AsyncServer(
    async_mode='asgi',
    cors_allowed_origins=settings.socket_cors_origin.split(","),
    ping_timeout=60,
    ping_interval=25
)

class SDIRSWebSocketManager:
    """
    SDIRS WebSocket Manager handles real-time coordination between
    the Citizen App, Responders, and the Emergency Command Center.
    """

    @staticmethod
    @sio.event
    async def connect(sid, environ):
        """
        WebSocket connection handler with JWT authentication.
        Verifies JWT token from Authorization header or query string.
        """
        # 1. Extract token from Authorization header or query string
        auth_header = environ.get('HTTP_AUTHORIZATION', '')
        token = auth_header.replace('Bearer ', '') if auth_header else None

        if not token:
            query_string = environ.get('QUERY_STRING', '')
            if query_string:
                params = parse_qs(query_string)
                token_params = params.get('token')
                if token_params:
                    token = token_params[0]

        # 2. Authenticate
        user_payload = None
        if token:
            user_payload = decode_access_token(token)
            if user_payload:
                logger.info("sdirs_client_authenticated", sid=sid, user=user_payload.get('sub'))
                # Save user info to session for later use
                async with sio.session(sid) as session:
                    session['user'] = user_payload
            else:
                logger.warning("sdirs_client_invalid_token", sid=sid)
        
        # 3. Enforcement
        if not user_payload:
            if settings.environment == 'production':
                logger.error("sdirs_client_rejected_auth_required", sid=sid)
                return False
            else:
                logger.warning("sdirs_client_connected_without_auth", sid=sid)

        logger.info("sdirs_client_connected", sid=sid)
        await sio.emit('connection_status', {'status': 'connected', 'sid': sid}, to=sid)
        
        # Send history to the newly connected client
        db = SessionLocal()
        try:
            # Get last 50 messages
            recent_messages = db.query(Message).order_by(Message.sent_at.desc()).limit(50).all()
            for msg in reversed(recent_messages):
                await sio.emit('receive_message', {
                    'sender_id': msg.sender_id,
                    'sender_name': msg.sender_name,
                    'text': msg.message_text,
                    'type': msg.message_type,
                    'timestamp': msg.sent_at.timestamp() * 1000
                }, to=sid)
        finally:
            db.close()

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
        Expected data: {'sender_name': str, 'incident_id': int, 'text': str, 'type': str}
        """
        async with sio.session(sid) as session:
            user = session.get('user')
            if not user:
                logger.warning("sdirs_message_rejected_not_authenticated", sid=sid)
                return

            # Authorize 'command' type messages (Only admin/ops/responder)
            msg_type = data.get('type', 'chat')
            user_role = user.get('role', 'citizen')
            if msg_type == 'command' and user_role not in ['admin', 'ops', 'responder']:
                logger.warning("sdirs_command_rejected_unauthorized", sid=sid, role=user_role)
                return

            logger.info(f"Message from {sid}: {data}")
            
            # Persist to database
            db = SessionLocal()
            try:
                # Find user ID from email (sub)
                user_email = user.get('sub')
                db_user = db.query(db_models.User).filter(db_models.User.email == user_email).first()
                user_id = db_user.id if db_user else None

                new_msg = Message(
                    sender_id=user_id,
                    sender_name=data.get('sender_name', user.get('sub', 'Anonymous')),
                    incident_id=data.get('incident_id'),
                    message_text=data.get('text', ''),
                    message_type=msg_type
                )

                db.add(new_msg)
                db.commit()
                db.refresh(new_msg)
                
                # Broadcast to all connected clients
                broadcast_data = {
                    'sender_id': new_msg.sender_id,
                    'sender_name': new_msg.sender_name,
                    'text': new_msg.message_text,
                    'type': new_msg.message_type,
                    'timestamp': new_msg.sent_at.timestamp() * 1000
                }
                await sio.emit('receive_message', broadcast_data)
            except Exception as e:
                logger.error(f"Error saving message: {e}")
                db.rollback()
            finally:
                db.close()

    @staticmethod
    @sio.event
    async def sos_alert(sid, data):
        """
        Module 1, 4 & 5: SOS Emergency Signal
        Broadcasts urgent SOS signal from a citizen to all responders and Command Center.
        """
        async with sio.session(sid) as session:
            user = session.get('user')
            if not user:
                logger.warning("sdirs_sos_rejected_not_authenticated", sid=sid)
                # Still allow SOS for non-authenticated users in dev, but log warning
                if settings.environment == 'production':
                    return

            logger.info(f"SOS ALERT from {sid}: {data}")
            
            # Persist to database
            db = SessionLocal()
            try:
                new_sos = SOSAlert(
                    name=data.get('name', user.get('sub', 'Anonymous')) if user else data.get('name', 'Anonymous'),
                    latitude=data.get('location', {}).get('latitude'),
                    longitude=data.get('location', {}).get('longitude'),
                    severity='high',
                    status='active'
                )
                db.add(new_sos)
                db.commit()
                db.refresh(new_sos)
                
                # Broadcast the SOS alert to everyone
                alert_data = {
                    'id': f"sos-{new_sos.id}",
                    'type': 'SOS EMERGENCY',
                    'message': f"URGENT: SOS signal from {new_sos.name}. Immediate assistance required.",
                    'severity': 'high',
                    'timestamp': new_sos.timestamp.timestamp() * 1000,
                    'location': {'latitude': new_sos.latitude, 'longitude': new_sos.longitude}
                }
                await sio.emit('emergency_alert', alert_data)
                
                # Also emit as a message for the chat history
                system_msg = {
                    'sender_id': 'system',
                    'sender_name': 'SDIRS SOS',
                    'text': f"🚨 SOS ALERT from {new_sos.name}!",
                    'type': 'broadcast',
                    'timestamp': new_sos.timestamp.timestamp() * 1000
                }
                await sio.emit('receive_message', system_msg)
                
            except Exception as e:
                logger.error(f"Error saving SOS alert: {e}")
                db.rollback()
            finally:
                db.close()

    @staticmethod
    @sio.event
    async def incident_reported(sid, data):
        """
        Triggered when a new incident is reported via the mobile app.
        """
        logger.info(f"New incident reported via socket: {data}")
        await sio.emit('emergency_alert', {
            'id': f"inc-{data.get('id', 'new')}",
            'type': f"New {data.get('type', 'Incident')}",
            'message': f"A new {data.get('type')} has been reported. Severity: {data.get('severity')}",
            'severity': data.get('severity', 'medium'),
            'timestamp': 0, # Should be real timestamp
            'location': data.get('location')
        })

    @staticmethod
    @sio.event
    async def send_location(sid, data):
        """
        Module 4 & 5: Real-Time Command Center & Resource Allocation
        Updates responder GPS locations on the live map.
        Expected data: {'name': str, 'role': str, 'coords': dict, 'timestamp': int}
        """
        # Add the unique session ID as the user ID for tracking
        data['id'] = sid
        # Broadcast to all connected clients as 'location_update'
        await sio.emit('location_update', data)

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
    async def prediction_alert(sid, data):
        """
        Module 1: Disaster Prediction Engine
        Broadcasts high-risk predictions to the Command Center.
        Expected data: {'type': str, 'location': dict, 'probability': float, 'level': str}
        """
        logger.info(f"Prediction Alert: {data}")
        await sio.emit('prediction_alert', data)

    @staticmethod
    async def broadcast_incident(data: dict):
        """
        Server-side utility to broadcast new incidents to all connected clients.
        Useful for calling from services or background tasks.
        """
        logger.info(f"Broadcasting incident: {data}")
        await sio.emit('emergency_alert', {
            'id': f"inc-{data.get('id', 'new')}",
            'type': f"New {data.get('type', 'Incident')}",
            'message': f"A new {data.get('type')} has been reported. Severity: {data.get('severity')}",
            'severity': data.get('severity', 'medium'),
            'timestamp': datetime.now().timestamp() * 1000,
            'location': data.get('location')
        })

    @staticmethod
    async def broadcast_prediction(data: dict):
        """
        Server-side utility to broadcast prediction alerts to all connected clients.
        """
        logger.info(f"Broadcasting prediction: {data}")
        await sio.emit('prediction_alert', data)

# Export the sio instance to be mounted in main.py
def get_sio_server():
    return sio
