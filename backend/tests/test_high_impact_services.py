import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from app.services.prediction_engine import PredictionEngine
from app.services.population_service import PopulationService
from app.services.hazard_aware_routing import HazardAwareRoutingService
from app.models.sqlalchemy import Incident
from sqlalchemy.orm import Session

# --- Prediction Engine Tests ---

@pytest.mark.asyncio
async def test_prediction_engine_nws_fallback():
    # Mock OWM key to be empty to force NWS fallback
    with patch("app.core.config.settings.openweathermap_api_key", ""), \
         patch("app.services.prediction_engine.PredictionEngine._fetch_nws_alerts") as mock_nws:
        
        mock_nws.return_value = {"source": "NWS", "temp": 20.0, "rainfall": 5.0}
        
        res = await PredictionEngine._fetch_weather_data(26.85, 80.95)
        assert res["source"] == "NWS"
        mock_nws.assert_called_once()

@pytest.mark.asyncio
async def test_prediction_engine_get_risks_no_model():
    # Test fallback logic when model is not loaded
    with patch("app.services.prediction_engine.PredictionEngine._load_model", return_value=None), \
         patch("app.services.prediction_engine.PredictionEngine._fetch_weather_data") as mock_weather, \
         patch("app.services.population_service.population_service.get_population_density", return_value=1000.0):
        
        mock_weather.return_value = {"source": "mock", "temp": 30.0, "rainfall": 40.0, "humidity": 20.0}
        
        resp = await PredictionEngine.get_disaster_risks(26.85, 80.95)
        assert len(resp.risks) > 0
        # High rainfall should lead to high/critical flood risk
        flood = next(r for r in resp.risks if r.disaster_type == "Flood")
        assert flood.probability > 0.5

def test_rainfall_calculation():
    # Test OWM rainfall calc
    mock_forecast = {
        "list": [
            {"rain": {"3h": 1.5}},
            {"rain": {"3h": 2.5}},
            {} # No rain
        ]
    }
    assert PredictionEngine._calculate_rainfall(mock_forecast) == 4.0
    
    # Test NWS rainfall calc
    mock_nws_forecast = {
        "properties": {
            "periods": [
                {"quantitativePrecipitation": {"value": 0.5}},
                {"probabilityOfPrecipitation": {"value": 50}} # Used if qpf is 0
            ]
        }
    }
    assert PredictionEngine._calculate_rainfall_from_nws(mock_nws_forecast) == 0.5

# --- Population Service Tests ---

@pytest.mark.asyncio
async def test_population_service_cache():
    service = PopulationService()
    service._cache["26.85,80.95"] = 555.5
    service._last_cache_update = MagicMock() # Will be truthy
    
    with patch("app.services.population_service.PopulationService._is_cache_valid", return_value=True):
        density = await service.get_population_density(26.85, 80.95)
        assert density == 555.5

@pytest.mark.asyncio
async def test_population_estimate_radius():
    service = PopulationService()
    with patch.object(service, "get_population_density", return_value=1000.0):
        pop = await service.estimate_population(26.85, 80.95, radius_km=5.0)
        # area = pi * (5 * 0.621)^2 ~= 3.14 * 9.6 ~= 30 sq miles
        # pop = 1000 * 30 ~= 30000
        assert pop > 25000 and pop < 35000

@pytest.mark.asyncio
async def test_fetch_census_density_success():
    service = PopulationService()
    
    # Mock geocoder response
    mock_geo_resp = MagicMock()
    mock_geo_resp.status_code = 200
    mock_geo_resp.json.return_value = {
        "result": {
            "addressMatches": [{
                "geographies": {
                    "Census Tracts": [{"STATE": "01", "COUNTY": "001", "TRACT": "123456"}]
                }
            }]
        }
    }
    
    # Mock census pop response
    # The code expects population = int(pop_data[1][0])
    mock_pop_resp = MagicMock()
    mock_pop_resp.status_code = 200
    mock_pop_resp.json.return_value = [["P1_001N", "NAME"], ["5000", "Tract 123456"]]

    
    with patch("httpx.AsyncClient.get") as mock_get:
        mock_get.side_effect = [mock_geo_resp, mock_pop_resp]
        
        density = await service._fetch_census_density(26.85, 80.95)
        # population=5000, area=2.0 -> density=2500
        assert density == 2500.0

def test_population_area_type():
    service = PopulationService()
    assert service.get_area_type(26.85, 80.95) == "suburban"


# --- Hazard Aware Routing Tests ---

@pytest.mark.asyncio
async def test_hazard_aware_routing_logic(db: Session):
    # 1. Setup mock hazard in DB
    hazard = Incident(
        id=101, title="Road Flood", incident_type="flood", 
        status="verified", latitude=26.8505, longitude=80.9505,
        predicted_severity="high"
    )
    db.add(hazard)
    db.flush()
    
    # 2. Mock Google Maps response with a route passing near the hazard
    mock_directions = {
        "status": "OK",
        "routes": [{
            "legs": [{
                "steps": [
                    {
                        "start_location": {"lat": 26.8500, "lng": 80.9500},
                        "end_location": {"lat": 26.8510, "lng": 80.9510}
                    }
                ]
            }]
        }]
    }
    
    with patch("app.services.google_maps_service.get_directions", return_value=mock_directions):
        result = await HazardAwareRoutingService.get_hazard_safe_route(db, "26.85,80.95", "26.86,80.96")
        
        assert "sdirs_hazards" in result
        assert len(result["sdirs_hazards"]) == 1
        assert result["sdirs_hazards"][0]["id"] == 101
        assert "hazard_warning" in result
        assert "CRITICAL" in result["hazard_warning"]

def test_route_near_point_helper():
    legs = [{
        "steps": [
            {
                "start_location": {"lat": 0.0, "lng": 0.0},
                "end_location": {"lat": 0.001, "lng": 0.001}
            }
        ]
    }]
    # Point exactly at start
    found, dist = HazardAwareRoutingService._is_route_near_point(legs, 0.0, 0.0, 0.1)
    assert found is True
    assert dist == 0
    
    # Point far away
    found, dist = HazardAwareRoutingService._is_route_near_point(legs, 1.0, 1.0, 0.1)
    assert found is False
    assert dist > 100 # km
