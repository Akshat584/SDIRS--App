import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.circuit_breaker import CircuitBreaker, CircuitState
from app.services.image_verification_service import ImageVerificationService
from app.services.weather_alert_service import get_weather_alert_data, _fetch_from_openweathermap
from app.services.google_maps_service import get_directions
from app.core.config import settings

# --- Circuit Breaker Tests ---

@pytest.mark.asyncio
async def test_circuit_breaker_flow():
    breaker = CircuitBreaker("TestBreaker", failure_threshold=2, recovery_timeout=1)
    
    # 1. Initially CLOSED
    assert breaker.state == CircuitState.CLOSED
    
    async def fail_func():
        raise Exception("Fail")
        
    async def success_func():
        return "OK"
        
    # 2. First failure
    with pytest.raises(Exception):
        await breaker.call(fail_func)
    assert breaker.failure_count == 1
    assert breaker.state == CircuitState.CLOSED
    
    # 3. Second failure -> OPEN
    with pytest.raises(Exception):
        await breaker.call(fail_func)
    assert breaker.state == CircuitState.OPEN
    
    # 4. Request while OPEN should be blocked
    res = await breaker.call(success_func)
    assert res is None
    
    # 5. Wait for recovery timeout
    import time
    breaker.last_failure_time = time.time() - 2 # Force timeout
    
    # 6. Should allow request and be HALF_OPEN
    assert breaker.allow_request() is True
    assert breaker.state == CircuitState.HALF_OPEN
    
    # 7. Success while HALF_OPEN -> CLOSED
    res = await breaker.call(success_func)
    assert res == "OK"
    assert breaker.state == CircuitState.CLOSED
    assert breaker.failure_count == 0

# --- Image Verification Service Tests ---

@pytest.mark.asyncio
async def test_image_verification_not_found():
    res = await ImageVerificationService.analyze_incident_image("non_existent.jpg")
    assert res["verified"] is False
    assert res["confidence"] == 0.0

@pytest.mark.asyncio
async def test_image_verification_success():
    with patch("os.path.exists", return_value=True), \
         patch("app.services.disaster_cv_model.disaster_cv_service.analyze_image") as mock_analyze:
        
        mock_analyze.return_value = {
            "verified": True, "confidence": 0.9, "labels": ["Fire"], "severity_boost": 0.3
        }
        
        res = await ImageVerificationService.analyze_incident_image("real_image.jpg")
        assert res["verified"] is True
        assert res["confidence"] == 0.9

# --- Weather Alert Service Tests ---

@pytest.mark.asyncio
async def test_weather_alert_no_key():
    with patch("app.core.config.settings.openweathermap_api_key", ""):
        res = await get_weather_alert_data(0, 0)
        assert res is None

@pytest.mark.asyncio
async def test_fetch_openweathermap_success():
    mock_data = {
        "lat": 0, "lon": 0, "timezone": "UTC", "timezone_offset": 0,
        "alerts": []
    }
    
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = mock_data
    
    with patch("httpx.AsyncClient.get", return_value=mock_resp):
        res = await _fetch_from_openweathermap(0, 0)
        assert res.lat == 0
        assert len(res.alerts) == 0

# --- Google Maps Service Tests ---

@pytest.mark.asyncio
async def test_google_maps_no_key():
    with patch("app.services.google_maps_service.GOOGLE_MAPS_API_KEY", None):
        res = await get_directions("A", "B")
        assert res is None

@pytest.mark.asyncio
async def test_google_maps_success():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"status": "OK", "routes": []}
    
    with patch("app.services.google_maps_service.GOOGLE_MAPS_API_KEY", "fake_key"), \
         patch("httpx.AsyncClient.get", return_value=mock_resp):
        
        res = await get_directions("A", "B")
        assert res["status"] == "OK"

@pytest.mark.asyncio
async def test_google_maps_error():
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"status": "REQUEST_DENIED", "error_message": "Invalid Key"}
    
    with patch("app.services.google_maps_service.GOOGLE_MAPS_API_KEY", "fake_key"), \
         patch("httpx.AsyncClient.get", return_value=mock_resp):
        
        res = await get_directions("A", "B")
        assert res is None
