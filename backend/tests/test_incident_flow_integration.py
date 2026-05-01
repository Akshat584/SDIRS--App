import pytest
import io
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from sqlalchemy.orm import Session
from app.models.sqlalchemy import Incident, User
from app.core.websockets import SDIRSWebSocketManager

@pytest.mark.asyncio
async def test_complete_incident_reporting_flow(client: TestClient, db: Session):
    """
    Integration Test: Full Incident Reporting Flow (Module 2, 3, 9)
    """
    # 1. Setup: Mock the background task, socket manager, and image validation
    with patch("app.services.background_tasks.BackgroundTaskManager.process_new_incident", new_callable=AsyncMock) as mock_bg, \
         patch("app.core.websockets.sio.emit", new_callable=AsyncMock) as mock_emit, \
         patch("app.api.incidents.validate_image_upload", new_callable=AsyncMock) as mock_val:
        
        mock_val.return_value = b"fake-validated-contents"
        
        # 2. Citizen reports an incident via API
        png_header = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
        response = client.post(
            "/api/incidents",
            data={
                "lat": 26.85,
                "lon": 80.95,
                "title": "Severe Flood",
                "description": "Water level is rising rapidly, help!",
                "incident_type": "flood"
            },
            files={"photo": ("flood.png", io.BytesIO(png_header), "image/png")}
        )
        
        if response.status_code != 201:
            print(f"DEBUG: Response Detail: {response.json()}")
        
        assert response.status_code == 201
        incident_id = response.json()["incident_id"]
        
        # 3. Verify incident was saved to DB
        incident = db.query(Incident).filter(Incident.id == incident_id).first()
        assert incident is not None
        assert incident.title == "Severe Flood"
        assert incident.incident_type == "flood"
        
        # 4. Verify background task was triggered
        mock_bg.assert_called_once()
        args, _ = mock_bg.call_args
        assert args[0] == incident_id
        assert args[1]["type"] == "flood"
        
        # 5. Simulate background task execution (AI verification + Broadcast)
        # In a real app, the background task would call SDIRSWebSocketManager.broadcast_incident
        incident_data = {"id": incident_id, "type": "flood", "severity": "high", "location": {"lat": 26.85, "lon": 80.95}}
        await SDIRSWebSocketManager.broadcast_incident(incident_data)
        
        # 6. Verify WebSocket broadcast was emitted
        # We expect 1 call from broadcast_incident
        assert mock_emit.called
        # Check if 'emergency_alert' was emitted
        any_emergency_alert = any(call.args[0] == 'emergency_alert' for call in mock_emit.call_args_list)
        assert any_emergency_alert is True

@pytest.mark.asyncio
async def test_responder_location_tracking_flow(client: TestClient):
    """
    Integration Test: Responder Location Tracking (Module 4, 5)
    """
    with patch("app.core.websockets.sio.emit", new_callable=AsyncMock) as mock_emit:
        # Simulate a responder sending location via WebSockets
        # Since we are testing the manager directly
        sid = "responder-sid-123"
        location_data = {
            "name": "Ambulance 01",
            "role": "responder",
            "coords": {"latitude": 26.85, "longitude": 80.95},
            "timestamp": 1625097600
        }
        
        await SDIRSWebSocketManager.send_location(sid, location_data)
        
        # Verify broadcast to all clients
        mock_emit.assert_called_with('location_update', {
            "name": "Ambulance 01",
            "role": "responder",
            "coords": {"latitude": 26.85, "longitude": 80.95},
            "timestamp": 1625097600,
            "id": sid
        })

@pytest.mark.asyncio
async def test_emergency_sos_flow(client: TestClient, db: Session):
    """
    Integration Test: Emergency SOS Signal (Module 1, 9)
    """
    # Create a mock session object
    session_data = {"user": {"sub": "sos_user@example.com", "role": "citizen"}}
    
    # Create a mock that acts as an async context manager
    class MockAsyncContextManager:
        async def __aenter__(self):
            return session_data
        async def __aexit__(self, exc_type, exc, tb):
            pass

    with patch("app.core.websockets.sio.emit", new_callable=AsyncMock) as mock_emit, \
         patch("app.core.websockets.sio.session", return_value=MockAsyncContextManager()), \
         patch("app.core.websockets.SessionLocal", return_value=db):
        
        sid = "citizen-sid-sos"
        sos_data = {
            "name": "John Doe",
            "location": {"latitude": 26.85, "longitude": 80.95}
        }
        
        await SDIRSWebSocketManager.sos_alert(sid, sos_data)
        
        # Verify 'emergency_alert' was emitted
        any_emergency_alert = any(call.args[0] == 'emergency_alert' for call in mock_emit.call_args_list)
        assert any_emergency_alert is True
        
        # Verify 'receive_message' system message was emitted
        any_system_msg = any(call.args[0] == 'receive_message' for call in mock_emit.call_args_list)
        assert any_system_msg is True
