import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.sqlalchemy import Message, Incident, User
from unittest.mock import patch, MagicMock

# --- Module 9: Messages Tests ---

def test_create_get_messages(client: TestClient, db: Session):
    # Create a message
    resp = client.post("/api/messages", json={
        "sender_id": 1,
        "message_text": "Need help at sector 4",
        "message_type": "chat",
        "incident_id": None
    })
    assert resp.status_code == 200
    msg_id = resp.json()["id"]
    
    # Get messages
    resp = client.get("/api/messages")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) >= 1
    assert any(m["id"] == msg_id for m in data)

def test_filter_messages(client: TestClient, db: Session):
    # Create different types of messages
    db.add(Message(sender_id=1, message_text="Chat 1", message_type="chat"))
    db.add(Message(sender_id=2, message_text="Broadcast 1", message_type="broadcast"))
    db.commit()
    
    resp = client.get("/api/messages?message_type=broadcast")
    assert resp.status_code == 200
    data = resp.json()
    assert all(m["message_type"] == "broadcast" for m in data)


# --- Module 3: NLP Analysis Tests ---

def test_analyze_incident_nlp(client: TestClient):
    # Test High Risk Keywords
    resp = client.post("/api/analyze", json={
        "description": "Explosion and trapped people",
        "image_uri": None
    })
    assert resp.status_code == 200
    assert resp.json()["severity"] == "critical"
    assert resp.json()["verified"] is True
    
    # Test Medium Risk (Flood)
    resp = client.post("/api/analyze", json={
        "description": "Water level is rising, flood here",
        "image_uri": "http://example.com/flood.jpg"
    })
    assert resp.status_code == 200
    assert resp.json()["severity"] in ["medium", "high", "critical"]
    assert "flood_detected" in resp.json()["ml_labels"]

    # Test with Image URI general fallback
    resp = client.post("/api/analyze", json={
        "description": "Something happened here",
        "image_uri": "http://example.com/random.jpg"
    })
    assert resp.status_code == 200
    assert "debris_detected" in resp.json()["ml_labels"]

# --- Module 4: Safe Zones Tests ---

@pytest.mark.asyncio
async def test_get_nearest_safe_zone(client: TestClient, db: Session):
    from app.models.sqlalchemy import SafeZone
    
    mock_sz = MagicMock(spec=SafeZone)
    mock_sz.id = 1
    mock_sz.name = "Safe Zone A"
    mock_sz.latitude = 26.85
    mock_sz.longitude = 80.95
    
    # Mock the DB utility AND the Google Maps service
    with patch("app.services.safe_zone_service.db_safe_zones.get_safe_zones") as mock_db_sz, \
         patch("app.services.safe_zone_service.get_directions") as mock_gmaps:
        
        mock_db_sz.return_value = [mock_sz]
        mock_gmaps.return_value = {
            "status": "OK",
            "routes": [{
                "legs": [{
                    "duration": {"value": 600, "text": "10 mins"},
                    "distance": {"text": "5 km"}
                }]
            }]
        }
        
        resp = client.get("/api/safe-zones/nearest?origin=26.84,80.94")
        assert resp.status_code == 200
        data = resp.json()
        assert data["safe_zone_name"] == "Safe Zone A"
        assert data["distance_text"] == "5 km"

def test_get_nearest_safe_zone_not_found(client: TestClient, db: Session):
    with patch("app.services.safe_zone_service.db_safe_zones.get_safe_zones") as mock_db_sz:
        mock_db_sz.return_value = []
        
        resp = client.get("/api/safe-zones/nearest?origin=26.84,80.94")
        assert resp.status_code == 404








# --- Notification Service: Deep Dive ---

@pytest.mark.asyncio
async def test_notification_service_triggers():
    from app.services.notification_service import NotificationService
    
    # We want to verify that trigger_omni_channel_alerts calls the 3 sub-methods
    with patch.object(NotificationService, "broadcast_to_dashboards") as mock_ws, \
         patch.object(NotificationService, "send_fcm_notifications") as mock_fcm, \
         patch.object(NotificationService, "send_authority_alerts") as mock_sms:
        
        await NotificationService.trigger_omni_channel_alerts(
            incident_id=999,
            nearby_data={"resources": [1, 2], "responders": [{"fcm_token": "abc"}]}
        )
        
        mock_ws.assert_called_once()
        mock_fcm.assert_called_once()
        mock_sms.assert_called_once()

@pytest.mark.asyncio
async def test_fcm_mock_behavior():
    from app.services.notification_service import NotificationService
    import firebase_admin
    
    # Ensure firebase_admin is NOT initialized to trigger mock path
    with patch("firebase_admin._apps", []):
        with patch("app.services.notification_service.logger") as mock_logger:
            await NotificationService.send_fcm_notifications(123, [{"fcm_token": "token"}])
            # Check if mock log was called
            mock_logger.info.assert_any_call("FCM (Mock): Sending push notifications to 1 nearby responders for incident 123.")

@pytest.mark.asyncio
async def test_twilio_mock_behavior():
    from app.services.notification_service import NotificationService
    from app.core.config import settings
    
    # Force missing settings to trigger mock
    with patch("app.core.config.settings.twilio_account_sid", None):
        with patch("app.services.notification_service.logger") as mock_logger:
            await NotificationService.send_authority_alerts(456)
            mock_logger.info.assert_any_call("Twilio (Mock): Sending SMS/Voice alerts to senior officials for incident 456.")
