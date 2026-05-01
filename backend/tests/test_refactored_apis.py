import pytest
from unittest.mock import patch, MagicMock

@pytest.fixture
def mock_google_maps():
    with patch("app.services.safe_zone_service.get_distance_matrix") as mock:
        mock.return_value = {
            "status": "OK",
            "rows": [{
                "elements": [
                    {
                        "status": "OK",
                        "duration": {"value": 600, "text": "10 mins"},
                        "distance": {"value": 5000, "text": "5 km"}
                    }
                ]
            }]
        }
        yield mock

def test_analytics_dashboard(client, auth_headers):
    response = client.get("/api/dashboard-metrics", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "performance" in data
    assert "trends" in data
    assert "utilization" in data
    assert "incident_types_distribution" in data

def test_create_incident_authenticated(client, auth_headers):
    # Mocking background tasks to avoid executing them during unit tests
    with patch("app.services.background_tasks.BackgroundTaskManager.process_new_incident") as mock_task:
        response = client.post(
            "/api/incidents",
            data={
                "lat": 26.8467,
                "lon": 80.9462,
                "title": "Test Incident",
                "description": "This is a test incident",
                "incident_type": "fire"
            },
            headers=auth_headers
        )
        assert response.status_code == 201
        assert response.json()["status"] == "success"
        assert "incident_id" in response.json()
        # Verify background task was triggered
        mock_task.assert_called_once()

def test_create_incident_unauthenticated(client):
    response = client.post(
        "/api/incidents",
        data={
            "lat": 26.8467,
            "lon": 80.9462,
            "title": "Test Incident"
        }
    )
    # Should fail as authentication is now required
    assert response.status_code == 401

def test_nearest_safe_zone(client, auth_headers, db, mock_google_maps):
    from app.models.sqlalchemy import SafeZone
    # Seed a safe zone for the test
    sz = SafeZone(name="Test Shelter", latitude=26.8588, longitude=80.9200, capacity=100)
    db.add(sz)
    db.commit()

    response = client.get("/api/safe-zones/nearest?origin=26.8467,80.9462", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["safe_zone_name"] == "Test Shelter"
    assert "distance_text" in data
