import pytest
from unittest.mock import patch, MagicMock
from app.services.disaster_cv_model import DisasterCVModel
from app.services.drone_sar_service import DroneSARService
from app.models.drone import DroneTelemetry
from datetime import datetime

def test_disaster_cv_model_mapping():
    # Mock YOLO model
    with patch("app.services.disaster_cv_model.YOLO") as mock_yolo:
        mock_yolo_inst = MagicMock()
        mock_yolo.return_value = mock_yolo_inst
        
        # Mock detection names
        mock_yolo_inst.names = {0: "person", 1: "fire", 2: "boat"}
        
        # Mock detection result
        mock_box1 = MagicMock()
        mock_box1.cls = [1] # fire
        mock_box1.conf = [0.9]
        
        mock_result = MagicMock()
        mock_result.boxes = [mock_box1]
        mock_yolo_inst.return_value = [mock_result]
        
        service = DisasterCVModel(model_path="yolov8n.pt")
        result = service.analyze_image("dummy_path.jpg")
        
        assert result["verified"] is True
        assert "Fire" in result["labels"]
        assert result["severity_boost"] > 0

def test_drone_sar_waypoints():
    waypoints = DroneSARService.generate_s_pattern_waypoints(
        min_lat=26.84, min_lon=80.94, max_lat=26.85, max_lon=80.95, step_degrees=0.005
    )
    assert len(waypoints) > 0
    assert waypoints[0]["lat"] == 26.84
    assert waypoints[0]["lon"] == 80.94

def test_drone_sar_telemetry_update():
    drone = DroneTelemetry(
        drone_id="DRN-01",
        lat=26.845, lon=80.945, altitude=100.0, speed=10.0,
        battery_percentage=100.0, status="searching",
        search_area=[26.84, 80.94, 26.85, 80.95],
        last_update=datetime.now()
    )
    
    initial_lon = drone.lon
    initial_lat = drone.lat
    DroneSARService.update_sar_telemetry(drone)

    # Position should change (waypoint movement)
    assert drone.lon != initial_lon or drone.lat != initial_lat

    assert drone.battery_percentage < 100.0
    assert drone.last_update is not None

@pytest.mark.asyncio
async def test_drone_sar_detection_mocked():
    # Mock YOLO to allow DisasterCVModel to load
    with patch("app.services.disaster_cv_model.YOLO") as mock_yolo:
        mock_yolo_inst = MagicMock()
        mock_yolo.return_value = mock_yolo_inst
        
        service = DroneSARService()
        assert service.cv_model.is_loaded is True
        
        # Mock analyze_image
        with patch.object(service.cv_model, "analyze_image") as mock_analyze:
            mock_analyze.return_value = {
                "verified": True, "confidence": 0.85, "labels": ["Fire/Smoke"], "severity_boost": 0.5
            }
            
            res = await service.detect_disaster_from_image(b"fake_image_bytes", 26.85, 80.95)
            
            assert res is not None
            assert res["type"] == "Fire/Smoke"
            assert res["confidence"] == 0.85
            assert res["lat"] == 26.85

