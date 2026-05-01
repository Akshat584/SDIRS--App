import pytest
import socketio
from main import app
import asyncio
from app.core.config import settings

@pytest.mark.asyncio
async def test_socket_connection():
    # In a real test we'd need to start the server or use a mock
    # But for a quick integration check of the SIO instance:
    from app.core.websockets import get_sio_server
    sio = get_sio_server()
    assert sio is not None
    assert sio.async_mode == 'asgi'

@pytest.mark.asyncio
async def test_socket_manager_logic():
    """
    Test the logic of WebSocket handlers directly without a full network stack.
    """
    from app.core.websockets import SDIRSWebSocketManager
    from unittest.mock import AsyncMock, patch, MagicMock
    
    # Mock sid and environ
    sid = "test_sid"
    environ = {
        'HTTP_AUTHORIZATION': 'Bearer mocked_token',
        'QUERY_STRING': ''
    }
    
    # Mock decode_access_token to return a user
    with patch("app.core.websockets.decode_access_token") as mock_decode:
        mock_decode.return_value = {"sub": "test_user", "role": "admin"}
        
        # Mock sio.session, sio.emit and SessionLocal
        with patch("app.core.websockets.sio.session") as mock_session, \
             patch("app.core.websockets.sio.emit") as mock_emit, \
             patch("app.core.websockets.SessionLocal") as mock_db_session:
            
            # Setup session mock context manager
            session_data = {}
            mock_session.return_value.__aenter__.return_value = session_data
            
            # Setup DB mock
            mock_db = MagicMock()
            mock_db_session.return_value = mock_db
            mock_db.query.return_value.order_by.return_value.limit.return_value.all.return_value = []
            
            # Call connect
            await SDIRSWebSocketManager.connect(sid, environ)
            
            # Verify user saved to session
            assert session_data['user']['sub'] == "test_user"
            
            # Verify connection_status emitted
            mock_emit.assert_any_call('connection_status', {'status': 'connected', 'sid': sid}, to=sid)

@pytest.mark.asyncio
async def test_send_message_socket():
    from app.core.websockets import SDIRSWebSocketManager
    from unittest.mock import AsyncMock, patch, MagicMock
    from datetime import datetime
    
    sid = "test_sid"
    data = {
        "sender_name": "Test User",
        "text": "Hello SDIRS",
        "type": "chat"
    }
    
    # Mock session data
    session_data = {'user': {'sub': 'test_user', 'role': 'citizen'}}
    
    with patch("app.core.websockets.sio.session") as mock_session, \
         patch("app.core.websockets.sio.emit") as mock_emit, \
         patch("app.core.websockets.SessionLocal") as mock_db_session, \
         patch("app.core.websockets.Message") as mock_message_cls:
        
        mock_session.return_value.__aenter__.return_value = session_data
        
        # Mock DB
        mock_db = MagicMock()
        mock_db_session.return_value = mock_db
        
        # Mock Message instance
        mock_msg_inst = MagicMock()
        mock_msg_inst.sent_at = datetime.now()
        mock_msg_inst.sender_id = "test_user"
        mock_msg_inst.sender_name = "Test User"
        mock_msg_inst.message_text = "Hello SDIRS"
        mock_msg_inst.message_type = "chat"
        mock_message_cls.return_value = mock_msg_inst
        
        await SDIRSWebSocketManager.send_message(sid, data)
        
        # Verify broadcast
        mock_emit.assert_called()
        # Find 'receive_message' call
        receive_msg_call = next((c for c in mock_emit.call_args_list if c.args[0] == 'receive_message'), None)
        assert receive_msg_call is not None
        assert receive_msg_call.args[1]['text'] == "Hello SDIRS"

@pytest.mark.asyncio
async def test_sos_alert_socket():
    from app.core.websockets import SDIRSWebSocketManager
    from unittest.mock import patch, MagicMock
    from datetime import datetime
    
    sid = "test_sid"
    data = {
        "name": "Citizen A",
        "location": {"latitude": 26.85, "longitude": 80.95}
    }
    
    with patch("app.core.websockets.sio.session") as mock_session, \
         patch("app.core.websockets.sio.emit") as mock_emit, \
         patch("app.core.websockets.SessionLocal") as mock_db_session, \
         patch("app.core.websockets.SOSAlert") as mock_sos_cls:
        
        mock_session.return_value.__aenter__.return_value = {} # No user in session
        
        # Mock DB
        mock_db = MagicMock()
        mock_db_session.return_value = mock_db
        
        # Mock SOSAlert instance
        mock_sos_inst = MagicMock()
        mock_sos_inst.id = 777
        mock_sos_inst.timestamp = datetime.now()
        mock_sos_inst.name = "Citizen A"
        mock_sos_inst.location_lat = 26.85
        mock_sos_inst.location_lon = 80.95
        mock_sos_cls.return_value = mock_sos_inst
        
        await SDIRSWebSocketManager.sos_alert(sid, data)
        
        # Verify broadcasts
        mock_emit.assert_called()
        # Should emit 'emergency_alert' and 'receive_message'
        events = [c.args[0] for c in mock_emit.call_args_list]
        assert 'emergency_alert' in events
        assert 'receive_message' in events

@pytest.mark.asyncio
async def test_send_location_socket():
    from app.core.websockets import SDIRSWebSocketManager
    from unittest.mock import patch
    
    sid = "sid_123"
    data = {
        "name": "Responder 1",
        "coords": {"lat": 26.85, "lon": 80.95}
    }
    
    with patch("app.core.websockets.sio.emit") as mock_emit:
        await SDIRSWebSocketManager.send_location(sid, data)
        
        mock_emit.assert_called_once_with('location_update', {
            "name": "Responder 1",
            "coords": {"lat": 26.85, "lon": 80.95},
            "id": sid
        })



@pytest.mark.asyncio
async def test_socket_connect_query_token():
    from app.core.websockets import SDIRSWebSocketManager
    from unittest.mock import patch, MagicMock
    
    sid = "sid_query"
    environ = {
        'QUERY_STRING': 'token=query_mocked_token'
    }
    
    with patch("app.core.websockets.decode_access_token") as mock_decode, \
         patch("app.core.websockets.sio.session") as mock_session, \
         patch("app.core.websockets.sio.emit"), \
         patch("app.core.websockets.SessionLocal"):
        
        mock_decode.return_value = {"sub": "query_user"}
        mock_session.return_value.__aenter__.return_value = {}
        
        await SDIRSWebSocketManager.connect(sid, environ)
        mock_decode.assert_called_with('query_mocked_token')

@pytest.mark.asyncio
async def test_socket_connect_prod_reject():
    from app.core.websockets import SDIRSWebSocketManager
    from unittest.mock import patch
    
    sid = "sid_prod"
    environ = {'QUERY_STRING': ''}
    
    with patch("app.core.config.settings.environment", "production"):
        res = await SDIRSWebSocketManager.connect(sid, environ)
        assert res is False

@pytest.mark.asyncio
async def test_socket_send_command_unauthorized():
    from app.core.websockets import SDIRSWebSocketManager
    from unittest.mock import patch
    
    sid = "sid_unauth"
    data = {"type": "command", "text": "REBOOT"}
    session_data = {'user': {'role': 'citizen'}}
    
    with patch("app.core.websockets.sio.session") as mock_session, \
         patch("app.core.websockets.sio.emit") as mock_emit:
        mock_session.return_value.__aenter__.return_value = session_data
        
        await SDIRSWebSocketManager.send_message(sid, data)
        # Should not emit if rejected
        mock_emit.assert_not_called()

@pytest.mark.asyncio
async def test_socket_disconnect():
    from app.core.websockets import SDIRSWebSocketManager
    await SDIRSWebSocketManager.disconnect("any_sid") # Just covers the line

@pytest.mark.asyncio
async def test_broadcast_methods():
    from app.core.websockets import SDIRSWebSocketManager
    from unittest.mock import patch
    
    with patch("app.core.websockets.sio.emit") as mock_emit:
        await SDIRSWebSocketManager.broadcast_incident({"id": 1})
        await SDIRSWebSocketManager.broadcast_prediction({"risk": "high"})
        
        assert mock_emit.call_count == 2

