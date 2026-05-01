import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models.sqlalchemy import User, Incident, Resource, Allocation, Message
from app.core.security import get_password_hash
import io
from unittest.mock import patch, MagicMock

@pytest.mark.asyncio
async def test_full_incident_flow_integration(client: TestClient, db: Session):
    """
    Integration test for Module 2 (Incidents) + Module 3 (Verification) + Module 10 (Severity prediction).
    """
    # 1. Setup - Create a responder and a citizen
    citizen = User(
        name="Citizen User",
        email="citizen@example.com",
        hashed_password=get_password_hash("password123"),
        role="citizen"
    )
    responder = User(
        name="Responder One",
        email="responder@example.com",
        hashed_password=get_password_hash("password123"),
        role="responder"
    )
    db.add_all([citizen, responder])
    db.commit()
    
    # Authenticate citizen
    login_resp = client.post("/api/auth/login", data={"username": citizen.email, "password": "password123"})
    assert login_resp.status_code == 200
    access_token = login_resp.json()["access_token"]
    auth_headers = {"Authorization": f"Bearer {access_token}"}
    
    # 2. Citizen reports an incident with a "photo"
    # Mocking AI CV results to be verified
    with patch("app.services.image_verification_service.ImageVerificationService.analyze_incident_image") as mock_cv:
        mock_cv.return_value = {
            "verified": True,
            "confidence": 0.95,
            "labels": ["Fire/Smoke"],
            "severity_boost": 0.2
        }
        
        # Mocking weather and population for severity prediction
        with patch("app.services.prediction_engine.PredictionEngine._fetch_weather_data") as mock_weather:
            mock_weather.return_value = {"temp": 35.0, "rainfall": 0.0, "wind_speed": 25.0}
            
            with patch("app.services.population_service.population_service.get_population_density") as mock_pop:
                mock_pop.return_value = 5000.0 # High density
                
                # Mock notifications to avoid hitting real APIs
                with patch("app.services.notification_service.NotificationService.trigger_omni_channel_alerts") as mock_notify:
                    
                    # Perform the incident report
                    from PIL import Image
                    import io
                    
                    # Create a real small image
                    img = Image.new('RGB', (10, 10), color = 'red')
                    img_byte_arr = io.BytesIO()
                    img.save(img_byte_arr, format='PNG')
                    img_byte_arr.seek(0)
                    
                    # Mock the severity model itself if it exists or its predict method
                    with patch("app.services.severity_service.severity_model") as mock_model:
                        mock_model.predict.return_value = [2] # 2 = HIGH in SEVERITY_MAPPING
                        
                        response = client.post(
                            "/api/incidents",
                            data={
                                "lat": 26.8467,
                                "lon": 80.9462,
                                "title": "Large Fire in Sector 5",
                                "description": "Building on fire, smoke everywhere",
                                "incident_type": "fire"
                            },
                            files={"photo": ("fire.png", img_byte_arr, "image/png")},
                            headers=auth_headers
                        )

                    
                    if response.status_code != 201:
                        print(f"DEBUG: Response Body: {response.json()}")
                    
                    assert response.status_code == 201

                    data = response.json()
                    assert data["status"] == "success"
                    incident_id = data["incident_id"]

                    # 2.5 Manually trigger background task (since it's async in production)
                    from app.services.background_tasks import BackgroundTaskManager
                    await BackgroundTaskManager.process_new_incident(incident_id, {})

                    # 3. Verify database state
                    db_incident = db.query(Incident).filter(Incident.id == incident_id).first()
                    assert db_incident is not None
                    assert db_incident.ai_verified is True
                    assert db_incident.ai_confidence == 0.95
                    # Severity should be high or critical given mock inputs
                    assert db_incident.predicted_severity in ["high", "critical"]
                    assert db_incident.status == "verified"
                    
                    # 4. Check if notifications were triggered
                    mock_notify.assert_called_once()
                    
                    # 5. Command Center / Responder views the incident
                    # Login as responder
                    resp_login = client.post("/api/auth/login", data={"username": responder.email, "password": "password123"})
                    resp_token = resp_login.json()["access_token"]
                    resp_headers = {"Authorization": f"Bearer {resp_token}"}
                    
                    # Get all incidents
                    inc_resp = client.get("/api/incidents", headers=resp_headers)
                    assert inc_resp.status_code == 200
                    all_incidents = inc_resp.json()
                    # Find our incident in the list
                    our_inc = next((i for i in all_incidents if i["id"] == incident_id), None)
                    assert our_inc is not None
                    assert our_inc["title"] == "Large Fire in Sector 5"

@pytest.mark.asyncio
async def test_disaster_prediction_to_heatmap_integration(client: TestClient):
    """
    Module 1 (Prediction) -> Module 8 (Heatmap)
    """
    # 1. Get predictions for an area
    pred_resp = client.get("/api/predict?lat=26.85&lon=80.95")
    assert pred_resp.status_code == 200
    pred_data = pred_resp.json()
    assert len(pred_data["risks"]) > 0
    
    # 2. Get heatmap for the same area
    # Heatmap should include points from PredictionEngine (mocked or real-simulated)
    heat_resp = client.get("/api/heatmap?lat=26.85&lon=80.95")
    assert heat_resp.status_code == 200
    heat_data = heat_resp.json()
    
    # Ensure some points are of type 'prediction'
    prediction_points = [p for p in heat_data["points"] if p["type"] == "prediction"]
    assert len(prediction_points) > 0
    
    # 3. Get pre-positioning suggestions
    pre_resp = client.get("/api/pre-positioning?lat=26.85&lon=80.95")
    assert pre_resp.status_code == 200
    pre_data = pre_resp.json()
    assert "suggestions" in pre_data
