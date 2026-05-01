import pytest
from unittest.mock import patch, MagicMock
from app.services.verification_service import cross_check_data, VerificationResult
from app.services.data_validator import DataValidator
from app.services.earthquake_service import get_earthquake_data
from app.models.earthquake import EarthquakeFeature, EarthquakeProperties, Geometry
from app.models.weather_alert import WeatherAlert
from app.models.social_media import Tweet
from datetime import datetime

# --- Verification Service Tests ---

@pytest.mark.asyncio
async def test_cross_check_earthquake_with_tweets():
    eq = MagicMock(spec=EarthquakeFeature)
    eq.properties = MagicMock(spec=EarthquakeProperties)
    eq.properties.mag = 5.0
    eq.properties.place = "Los Angeles"
    eq.properties.title = "M 5.0 - LA"
    
    # 1. Confirmed by many tweets
    tweets = [Tweet(url="u", date=datetime.now(), content="Earthquake in Los Angeles!", username="u") for _ in range(6)]
    res = await cross_check_data(earthquakes=[eq], tweets=tweets)
    assert res[0].confidence == 0.9
    
    # 2. Confirmed by few tweets
    tweets = [Tweet(url="u", date=datetime.now(), content="Los Angeles shaking", username="u")]
    res = await cross_check_data(earthquakes=[eq], tweets=tweets)
    assert res[0].confidence == 0.7

    
    # 3. No tweets
    res = await cross_check_data(earthquakes=[eq], tweets=[])
    assert res[0].confidence == 0.6

@pytest.mark.asyncio
async def test_cross_check_flood_with_tweets():
    alert = MagicMock(spec=WeatherAlert)
    alert.event = "Flood Warning"
    alert.description = "River rising"
    
    # 1. Confirmed by many tweets
    tweets = [Tweet(url="u", date=datetime.now(), content="Flood Warning near river!", username="u") for _ in range(6)]
    res = await cross_check_data(weather_alerts=[alert], tweets=tweets)
    assert res[0].event_type == "Flood"
    assert res[0].confidence == 0.85
    
    # 2. No tweets
    res = await cross_check_data(weather_alerts=[alert], tweets=[])
    assert res[0].confidence == 0.6

# --- Data Validator Extended Tests ---

def test_data_validator_weather_errors():
    # Test multiple weather errors
    bad_weather = {
        "temp": 100,
        "humidity": 150,
        "rainfall": -10,
        "wind_speed": 200
    }
    res = DataValidator.validate_weather(bad_weather)
    assert res.is_valid is False
    assert "Temperature" in res.message
    assert "Humidity" in res.message
    assert "Rainfall" in res.message
    assert "Wind speed" in res.message

def test_data_validator_earthquake_errors():
    assert DataValidator.validate_earthquake({}).is_valid is False
    assert DataValidator.validate_earthquake({"geometry": {}}).is_valid is False
    
    bad_mag = {"geometry": {}, "properties": {"mag": 15}}
    assert DataValidator.validate_earthquake(bad_mag).is_valid is False
    
    bad_coords = {"properties": {"mag": 5}, "geometry": {"coordinates": [200, 100]}}
    assert DataValidator.validate_earthquake(bad_coords).is_valid is False

def test_data_validator_timestamp():
    future = datetime.now().replace(year=datetime.now().year + 1)
    assert DataValidator.validate_timestamp(future).is_valid is False
    
    old = datetime.now().replace(year=datetime.now().year - 1)
    assert DataValidator.validate_timestamp(old).is_valid is False

def test_data_validator_incident_report_errors():
    assert DataValidator.validate_incident_report({}).is_valid is False
    
    bad_severity = {
        "title": "T", "description": "D", "lat": 0, "lon": 0, "severity": "super-critical"
    }
    assert DataValidator.validate_incident_report(bad_severity).is_valid is False

def test_data_validator_batch_sensors():
    sensors = [
        {"type": "seismic", "current_value": 5.0},
        {"type": "smoke", "current_value": -1.0},
        {"type": "unknown"}
    ]
    res = DataValidator.validate_batch_sensors(sensors)
    assert len(res["valid"]) == 1
    assert len(res["invalid"]) == 1
    assert len(res["unknown"]) == 1

# --- Earthquake Service Error Test ---

@pytest.mark.asyncio
async def test_earthquake_service_error():
    with patch("app.services.earthquake_service._fetch_from_usgs", side_effect=Exception("API Error")):
        res = await get_earthquake_data()
        assert res is None
