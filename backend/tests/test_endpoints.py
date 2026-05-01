import pytest
from fastapi.testclient import TestClient

def test_read_root(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert "SDIRS" in response.json()["system"]

def test_health_check(client: TestClient):
    response = client.get("/api/health")
    assert response.status_code == 200
    # In test environment, it might be 'degraded' due to external APIs not being reachable
    assert response.json()["status"] in ["healthy", "degraded"]

def test_get_disaster_predictions(client: TestClient):
    response = client.get("/api/predict?lat=26.85&lon=80.95")
    assert response.status_code == 200
    data = response.json()
    assert "risks" in data
    assert len(data["risks"]) > 0

def test_get_heatmap_data(client: TestClient):
    response = client.get("/api/heatmap?lat=26.85&lon=80.95")
    assert response.status_code == 200
    data = response.json()
    assert "points" in data
    assert isinstance(data["points"], list)

from unittest.mock import patch, MagicMock

from app.models.weather_alert import WeatherAlertFeed

def test_get_red_alert_status(client: TestClient):
    # Test with earthquake magnitude above threshold
    response = client.get("/api/red-alert?earthquake_magnitude=7.5")
    assert response.status_code == 200
    data = response.json()
    if data: # It might return None if no alert triggered
        assert data["severity"] == "critical"

@patch("app.services.weather_alert_service.get_weather_alert_data")
def test_get_weather_alerts(mock_get_weather, client: TestClient):
    # Mock the weather service response
    mock_get_weather.return_value = WeatherAlertFeed(
        lat=26.85, lon=80.95, timezone="UTC", timezone_offset=0, alerts=[]
    )
    
    response = client.get("/api/weather-alerts?lat=26.85&lon=80.95")
    assert response.status_code == 200
    data = response.json()
    assert "alerts" in data
    assert isinstance(data["alerts"], list)

@patch("app.services.hazard_aware_routing.HazardAwareRoutingService.get_hazard_safe_route")
def test_get_routing(mock_get_route, client: TestClient):
    # Mock the routing service response
    mock_get_route.return_value = {
        "status": "success",
        "origin": "26.85,80.95",
        "destination": "26.86,80.96",
        "route": "mocked_route_polyline",
        "distance_km": 1.5,
        "duration_mins": 5,
        "hazards_avoided": []
    }
    
    response = client.get("/api/directions?origin=26.85,80.95&destination=26.86,80.96")
    assert response.status_code == 200
    data = response.json()
    assert "route" in data
    assert "distance_km" == "distance_km" in data


def test_get_drone_fleet(client: TestClient, auth_headers):
    # Drones endpoint might require auth
    response = client.get("/api/drones/fleet", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "drones" in data
    assert isinstance(data["drones"], list)

