import pytest
from unittest.mock import patch, MagicMock
from app.services.thingspeak_service import ThingSpeakService, HybridIoTService
import httpx

@pytest.mark.asyncio
async def test_thingspeak_fetch_latest_success():
    service = ThingSpeakService(channel_id="123", read_key="key")
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"field1": "5.5", "created_at": "2023-01-01T00:00:00Z"}
    
    with patch("httpx.AsyncClient.get", return_value=mock_resp):
        res = await service.fetch_latest()
        assert res["field1"] == "5.5"

@pytest.mark.asyncio
async def test_thingspeak_fetch_latest_fail():
    service = ThingSpeakService(channel_id="123")
    with patch("httpx.AsyncClient.get", side_effect=httpx.HTTPError("Error")):
        res = await service.fetch_latest()
        assert res is None

@pytest.mark.asyncio
async def test_thingspeak_fetch_multiple():
    service = ThingSpeakService(channel_id="123")
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"feeds": [{"f1": 1}, {"f1": 2}]}
    
    with patch("httpx.AsyncClient.get", return_value=mock_resp):
        res = await service.fetch_multiple(results=2)
        assert len(res) == 2

def test_thingspeak_mapping():
    service = ThingSpeakService()
    data = {
        "field1": "5.0", # seismic
        "field2": "1.5", # water
        "field3": "100", # smoke
        "field4": "25.0", # temp
        "field5": "50.0", # humidity
        "created_at": "now"
    }
    sensors = service.map_thingpeak_to_sensors(data)
    assert len(sensors) == 5
    types = [s["type"] for s in sensors]
    assert "seismic" in types
    assert "humidity" in types

def test_thingspeak_mapping_invalid():
    service = ThingSpeakService()
    data = {
        "field1": "invalid",
        "field2": "100.0" # out of range (max 20)
    }
    sensors = service.map_thingpeak_to_sensors(data)
    assert len(sensors) == 0

@pytest.mark.asyncio
async def test_hybrid_iot_service():
    hybrid = HybridIoTService()
    assert hybrid.thingspeak is None
    
    hybrid.enable_thingspeak("123", "key")
    assert hybrid._use_thingspeak is True
    assert hybrid.thingspeak.channel_id == "123"
    
    with patch.object(hybrid.thingspeak, "fetch_latest", return_value={"field1": "7.0"}):
        val = await hybrid.get_sensor_reading("seismic")
        assert val == 7.0
        
        all_s = await hybrid.get_all_sensors()
        assert len(all_s) == 1
        assert all_s[0]["type"] == "seismic"

@pytest.mark.asyncio
async def test_hybrid_iot_no_real_data():
    hybrid = HybridIoTService()
    val = await hybrid.get_sensor_reading("seismic")
    assert val is None
    
    all_s = await hybrid.get_all_sensors()
    assert all_s == []
