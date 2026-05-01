import pytest
import httpx
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.earthquake_service import get_earthquake_data
from app.services.weather_alert_service import get_weather_alert_data
from app.services.iot_sensor_service import iot_service
from app.models.earthquake import EarthquakeFeed
from app.models.weather_alert import WeatherAlertFeed

@pytest.mark.asyncio
async def test_earthquake_service_success():
    # Mock data with all required Pydantic fields
    mock_data = {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "properties": {
                    "mag": 5.2, 
                    "place": "10km E of Test", 
                    "time": 123456789, 
                    "url": "http://example.com",
                    "tsunami": 0,
                    "magType": "ml",
                    "type": "earthquake",
                    "title": "M 5.2 - Test"
                },
                "geometry": {"type": "Point", "coordinates": [80.95, 26.85, 10.0]},
                "id": "test1"
            }
        ]
    }
    
    with patch("app.services.earthquake_service._fetch_from_usgs") as mock_fetch:
        mock_fetch.return_value = EarthquakeFeed(**mock_data)
        
        result = await get_earthquake_data()
        assert result is not None
        assert len(result.features) == 1
        assert result.features[0].properties.mag == 5.2


@pytest.mark.asyncio
async def test_weather_alert_service_success():
    mock_data = {
        "lat": 26.85, "lon": 80.95, "timezone": "UTC", "timezone_offset": 0,
        "alerts": [
            {"event": "Flood Warning", "description": "High water", "start": 123, "end": 456, "sender_name": "Test"}
        ]
    }
    
    with patch("app.services.weather_alert_service._fetch_from_openweathermap") as mock_fetch:
        mock_fetch.return_value = WeatherAlertFeed(**mock_data)
        
        result = await get_weather_alert_data(26.85, 80.95)
        assert result is not None
        assert len(result.alerts) == 1
        assert result.alerts[0].event == "Flood Warning"

@pytest.mark.asyncio
async def test_iot_sensor_service_logic():
    # Test sensor initialization
    sensors = iot_service.get_all_sensors()
    assert len(sensors) > 0
    assert "seismic-01" in [s.id for s in sensors]
    
    # Test update simulation
    iot_service.update_simulated_sensors()
    # Check if values changed (likely they will because of random)
    
    # Test manual update
    iot_service.update_sensor_value("seismic-01", 6.5)
    s = next(s for s in iot_service.get_all_sensors() if s.id == "seismic-01")
    assert s.current_value == 6.5

@pytest.mark.asyncio
async def test_iot_thingspeak_mocked():
    # Mock thingspeak fetch
    with patch("app.services.iot_sensor_service.hybrid_iot_service.get_all_sensors") as mock_hybrid:
        mock_hybrid.return_value = [{"type": "seismic", "value": 7.8}]
        
        success = await iot_service._fetch_from_thingspeak()
        assert success
        
        # Verify local sensor updated
        s = next(s for s in iot_service.get_all_sensors() if s.id == "seismic-01")
        assert s.current_value == 7.8
        assert s.data_source == "thingspeak"
