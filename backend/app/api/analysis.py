from fastapi import APIRouter, HTTPException
from typing import List, Optional
from app.models.incident import IncidentAnalysisRequest, IncidentAnalysisResponse
from app.services.severity_service import predict_severity, Severity

router = APIRouter()

@router.post("/analyze", response_model=IncidentAnalysisResponse)
async def analyze_incident(data: IncidentAnalysisRequest):
    """
    AI-powered incident analysis endpoint.
    Determines severity, verification status, and labels based on description and image.
    """
    try:
        text_lower = data.description.lower()
        
        # 1. NLP Severity Analysis using rules + predict_severity
        # Mocking demographic/weather data for predict_severity
        # In a production app, these would come from real external APIs based on lat/lon
        temp = 30.0
        rainfall = 50.0
        wind_speed = 15.0
        pop_density = 1000.0
        historical_freq = 2.0
        
        # Keywords that override basic ML for higher sensitivity
        high_risk_keywords = ['trapped', 'dying', 'explosion', 'collapsed', 'severe', 'help']
        medium_risk_keywords = ['broken', 'no power', 'blocked', 'smoke', 'flood']
        
        # Get base severity from Random Forest model
        base_severity = predict_severity(temp, rainfall, wind_speed, pop_density, historical_freq)
        severity_str = base_severity.value
        
        # Apply keyword-based boosts
        if any(w in text_lower for w in high_risk_keywords):
            severity_str = Severity.HIGH.value
        elif any(w in text_lower for w in medium_risk_keywords) and severity_str == Severity.LOW.value:
            severity_str = Severity.MEDIUM.value

        # 2. Computer Vision / ML Labeling Simulation
        ml_labels = []
        if data.image_uri:
            if 'fire' in text_lower or 'smoke' in text_lower:
                ml_labels = ['fire_detected', 'smoke_presence']
            elif 'flood' in text_lower or 'water' in text_lower:
                ml_labels = ['flood_detected', 'water_hazard']
            else:
                ml_labels = ['debris_detected', 'infrastructure_damage']
        
        return {
            "severity": severity_str,
            "verified": severity_str in [Severity.HIGH.value, Severity.CRITICAL.value],
            "ml_labels": ml_labels
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
