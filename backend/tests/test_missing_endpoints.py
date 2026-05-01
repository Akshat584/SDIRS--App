import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from app.models.earthquake import EarthquakeFeed
from app.services.safe_zone_service import NearestSafeZoneResult
from app.models.sqlalchemy import Message, User
from sqlalchemy.orm import Session

def test_analyze_incident(client: TestClient):
    # Test valid analysis
    response = client.post(
        "/api/analyze",
        json={
            "description": "Severe fire in the building, help!",
            "image_uri": "http://example.com/fire.jpg"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["severity"] == "high"
    assert data["verified"] is True
    assert "fire_detected" in data["ml_labels"]

    # Test with different keywords
    response = client.post(
        "/api/analyze",
        json={
            "description": "Road is blocked by debris.",
            "image_uri": "http://example.com/road.jpg"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["severity"] == "medium"
    assert "debris_detected" in data["ml_labels"]

@patch("app.services.earthquake_service.get_earthquake_data")
def test_get_earthquakes(mock_get_eq, client: TestClient):
    mock_get_eq.return_value = EarthquakeFeed(
        type="FeatureCollection",
        metadata={"title": "USGS Earthquakes"},
        features=[]
    )
    response = client.get("/api/earthquakes")
    assert response.status_code == 200
    assert response.json()["type"] == "FeatureCollection"

@patch("app.services.safe_zone_service.find_nearest_safe_zone")
def test_get_nearest_safe_zone(mock_safe_zone, client: TestClient):
    mock_safe_zone.return_value = NearestSafeZoneResult(
        safe_zone_id=1, 
        safe_zone_name="Safe School", 
        distance_text="0.5 km", 
        duration_text="10 mins",
        route_url="http://maps.google.com/mock"
    )
    response = client.get("/api/safe-zones/nearest?origin=26.84,80.94")
    assert response.status_code == 200
    assert response.json()["safe_zone_name"] == "Safe School"

def test_get_messages(client: TestClient, db: Session):
    # Setup: Add a test message
    msg = Message(
        message_text="Hello Test", 
        message_type="chat", 
        incident_id=1,
        sender_id=1
    )
    db.add(msg)
    db.commit()

    response = client.get("/api/messages?incident_id=1")
    assert response.status_code == 200
    assert len(response.json()) >= 1
    assert response.json()[0]["message_text"] == "Hello Test"

def test_create_message(client: TestClient):
    response = client.post(
        "/api/messages",
        json={
            "message_text": "API Created Message",
            "message_type": "broadcast",
            "sender_id": 1,
            "incident_id": None
        }
    )
    assert response.status_code == 200
    assert response.json()["message_text"] == "API Created Message"

def test_read_incidents_authorized(client: TestClient, auth_headers, db: Session):
    # First, make sure the test user has responder role if needed
    # (The test_user fixture usually creates a citizen)
    # Let's check who the current user is
    me_resp = client.get("/api/auth/me", headers=auth_headers)
    user_email = me_resp.json()["email"]
    
    db_user = db.query(User).filter(User.email == user_email).first()
    db_user.role = "responder"
    db.commit()

    response = client.get("/api/incidents", headers=auth_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_read_incidents_unauthorized(client: TestClient, auth_headers, db: Session):
    # Demote user to citizen
    me_resp = client.get("/api/auth/me", headers=auth_headers)
    user_email = me_resp.json()["email"]
    
    db_user = db.query(User).filter(User.email == user_email).first()
    db_user.role = "citizen"
    db.commit()

    response = client.get("/api/incidents", headers=auth_headers)
    # RoleChecker should raise 403 Forbidden
    assert response.status_code == 403

def test_assign_drone_sar(client: TestClient):
    response = client.post(
        "/api/drones/SDIRS-DRN-01/assign-sar?min_lat=26.8&min_lon=80.9&max_lat=26.9&max_lon=81.0"
    )
    assert response.status_code == 200
    assert "SAR mission assigned" in response.json()["message"]

def test_drone_telemetry(client: TestClient):
    telemetry_data = {
        "drone_id": "SDIRS-DRN-99",
        "lat": 26.85,
        "lon": 80.95,
        "altitude": 100.0,
        "speed": 20.0,
        "battery_percentage": 50,
        "status": "returning",
        "last_update": "2026-04-16T12:00:00"
    }
    response = client.post(
        "/api/drones/SDIRS-DRN-99/telemetry",
        json=telemetry_data
    )
    assert response.status_code == 200
    assert response.json()["status"] in ["success", "created"]
