import pytest
from app.services.data_validator import DataValidator
from app.services.population_service import population_service
from app.services.severity_service import get_earthquake_severity, Severity

def test_data_validator():
    # Test valid sensor readings
    assert DataValidator.validate_sensor_reading("seismic", 5.0).is_valid
    assert DataValidator.validate_sensor_reading("water_level", 2.0).is_valid
    assert DataValidator.validate_sensor_reading("smoke", 50.0).is_valid
    
    # Test invalid sensor readings
    assert not DataValidator.validate_sensor_reading("seismic", -1.0).is_valid
    assert not DataValidator.validate_sensor_reading("water_level", 25.0).is_valid
    assert not DataValidator.validate_sensor_reading("smoke", -10.0).is_valid

@pytest.mark.asyncio
async def test_population_service():
    density = await population_service.get_population_density(26.85, 80.95)
    assert density > 0
    
    # Test cached or known areas
    density2 = await population_service.get_population_density(26.85, 80.95)
    assert density == density2

def test_earthquake_severity():
    assert get_earthquake_severity(7.5) == Severity.CRITICAL
    assert get_earthquake_severity(6.0) == Severity.HIGH
    assert get_earthquake_severity(4.0) == Severity.MEDIUM
    assert get_earthquake_severity(2.0) == Severity.LOW

from app.services.notification_service import NotificationService
import unittest.mock as mock
from unittest.mock import MagicMock
from app.services.resource_allocation_ai import ResourceAllocationAI
from app.models.sqlalchemy import Resource, User, Incident, Allocation
from app.models.incident import Location
from sqlalchemy.orm import Session

@pytest.mark.asyncio
async def test_notification_service_mocked():
    with mock.patch("app.services.notification_service.NotificationService.send_fcm_notifications") as mock_fcm:
        mock_fcm.return_value = None # It returns None but we check if it was called
        await NotificationService.send_fcm_notifications(101, [{"fcm_token": "test-token"}])
        mock_fcm.assert_called_once()

def test_get_nearby_responders(db: Session):
    # Setup: Create some resources and responders
    res1 = Resource(name="Near Ambulance", resource_type="ambulance", status="available", latitude=26.85, longitude=80.95)
    res2 = Resource(name="Far Ambulance", resource_type="ambulance", status="available", latitude=27.85, longitude=81.95)
    user1 = User(
        name="Near Responder", 
        email="near_resp@example.com", 
        hashed_password="hashed", 
        role="responder", 
        status="active", 
        latitude=26.85, 
        longitude=80.95
    )
    
    db.add_all([res1, res2, user1])
    db.commit()

    
    loc = Location(lat=26.8467, lon=80.9462)
    nearby = ResourceAllocationAI.get_nearby_responders(db, loc, radius_km=10.0)
    
    assert len(nearby["resources"]) == 1
    assert nearby["resources"][0].name == "Near Ambulance"
    assert len(nearby["responders"]) == 1
    assert nearby["responders"][0].name == "Near Responder"

def test_suggest_prepositioning():
    mock_risk = MagicMock()
    mock_risk.alert_level = "critical"
    mock_risk.disaster_type = "Flood"
    mock_risk.probability = 0.8
    mock_risk.area = "Zone A"
    
    suggestions = ResourceAllocationAI.suggest_prepositioning(None, [mock_risk])
    assert len(suggestions) == 1
    assert suggestions[0]["recommended_resource"] == "rescue_boat"
    assert suggestions[0]["suggested_count"] == 2

@pytest.mark.asyncio
async def test_find_best_resources(db: Session):
    # Setup
    incident = Incident(title="Big Fire", incident_type="fire", predicted_severity="high", latitude=26.85, longitude=80.95)
    db.add(incident)
    db.commit()
    
    # Resource 1: Perfect match
    r1 = Resource(
        name="Perfect Fire Truck", resource_type="fire_truck", status="available", 
        latitude=26.851, longitude=80.951, capacity=5, current_workload=0,
        specialized_skills=["firefighter"]
    )
    # Resource 2: Far away
    r2 = Resource(
        name="Far Ambulance", resource_type="ambulance", status="available", 
        latitude=27.85, longitude=81.95, capacity=2, current_workload=0
    )
    # Resource 3: Busy
    r3 = Resource(
        name="Busy Truck", resource_type="fire_truck", status="maintenance", 
        latitude=26.85, longitude=80.95
    )
    
    db.add_all([r1, r2, r3])
    db.commit()
    
    allocated_ids = await ResourceAllocationAI.find_best_resources(db, incident.id)
    
    # High severity needs 3 resources, but we only have 2 available candidates (r1, r2)
    assert len(allocated_ids) == 2
    assert r1.id in allocated_ids
    assert r2.id in allocated_ids
    
    # Verify r1 status updated
    db.refresh(r1)
    assert r1.status == "deployed"
    assert r1.current_workload == 1


def test_data_validator_extended():
    # Test Coordinates
    assert DataValidator.validate_coordinates(26.85, 80.95).is_valid
    assert not DataValidator.validate_coordinates(100, 80.95).is_valid
    assert not DataValidator.validate_coordinates(26.85, 200).is_valid
    
    # Test Weather
    assert DataValidator.validate_weather({"temp": 25, "humidity": 50}).is_valid
    assert not DataValidator.validate_weather({"temp": 150}).is_valid
    assert not DataValidator.validate_weather({"humidity": -10}).is_valid
    
    # Test Earthquake
    valid_eq = {
        "geometry": {"coordinates": [80.95, 26.85]},
        "properties": {"mag": 5.5}
    }
    assert DataValidator.validate_earthquake(valid_eq).is_valid
    assert not DataValidator.validate_earthquake({"properties": {"mag": 15}}).is_valid
    
    # Test Incident Report
    valid_report = {
        "title": "Fire",
        "description": "Large fire",
        "lat": 26.85,
        "lon": 80.95,
        "severity": "high"
    }
    assert DataValidator.validate_incident_report(valid_report).is_valid
    assert not DataValidator.validate_incident_report({"title": "Fire"}).is_valid # Missing fields
    
    # Test Sanitization
    assert DataValidator.sanitize_user_input("  hello  ") == "hello"
    assert DataValidator.sanitize_user_input("a" * 2000, max_length=10) == "a" * 10

