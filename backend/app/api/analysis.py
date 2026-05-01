from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional
from app.models.incident import IncidentAnalysisRequest, IncidentAnalysisResponse
from app.services.severity_service import predict_severity, Severity
from app.services.image_verification_service import ImageVerificationService
from app.services.prediction_engine import PredictionEngine
from app.services.population_service import population_service
from app.services import severity_service

router = APIRouter()

@router.post("/analyze", response_model=IncidentAnalysisResponse)
async def analyze_incident(data: IncidentAnalysisRequest):
    """
    AI-powered incident analysis endpoint.
    Determines severity, verification status, and labels based on description and image.
    """
    try:
        # 1. Computer Vision / ML Labeling (Module 3)
        ml_labels = []
        ai_verified = False
        ai_confidence = 0.0
        
        if data.image_uri:
            # Note: image_uri here could be a local path or a remote URL 
            # In this prototype, we'll try to analyze it if it's accessible
            try:
                # This assumes image_uri might be a path or we need to download it
                # For the demo, we'll try to analyze it if it exists locally
                local_path = data.image_uri.lstrip("/")
                import os
                if os.path.exists(local_path):
                    ai_results = await ImageVerificationService.analyze_incident_image(local_path)
                    ml_labels = ai_results.get("labels", [])
                    ai_verified = ai_results.get("verified", False)
                    ai_confidence = ai_results.get("confidence", 0.0)
            except Exception as e:
                print(f"Analysis API: CV failure: {e}")

        # 2. ML Severity Prediction (Module 10)
        # Fetch REAL weather and population data based on lat/lon
        weather_data = await PredictionEngine._fetch_weather_data(data.latitude, data.longitude)
        pop_density = await population_service.get_population_density(data.latitude, data.longitude)
        
        # Using the pre-trained .joblib model
        predicted_sev_enum = severity_service.predict_severity(
            temp=weather_data.get("temp", 25.0), 
            rainfall=weather_data.get("rainfall", 0.0), 
            wind_speed=weather_data.get("wind_speed", 5.0), 
            pop_density=pop_density, 
            historical_freq=2.0
        )
        severity_str = predicted_sev_enum.value
        
        # Override with high-risk keywords for safety
        text_lower = data.description.lower()
        high_risk_keywords = ['trapped', 'dying', 'explosion', 'collapsed', 'severe', 'help']
        if any(w in text_lower for w in high_risk_keywords):
            severity_str = Severity.CRITICAL.value

        return {
            "severity": severity_str,
            "verified": ai_verified or severity_str in [Severity.HIGH.value, Severity.CRITICAL.value],
            "ml_labels": ml_labels
        }
    except Exception as e:
        print(f"Analysis API Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
