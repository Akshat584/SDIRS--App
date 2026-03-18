from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy.orm import Session
from app.services.prediction_engine import PredictionEngine
from app.services.resource_allocation_ai import ResourceAllocationAI
from app.models.prediction import PredictionResponse
from app.db.database import get_db

router = APIRouter()

@router.get("/predict", response_model=PredictionResponse)
async def get_disaster_prediction(
    lat: float = Query(..., description="Latitude for risk analysis"),
    lon: float = Query(..., description="Longitude for risk analysis")
):
    """
    SDIRS Prediction Engine (Module 1): Get AI-powered disaster risks for a specific location.
    """
    try:
        prediction = await PredictionEngine.get_disaster_risks(lat, lon)
        return prediction
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pre-positioning")
async def get_prepositioning_suggestions(
    lat: float = Query(..., description="Latitude for regional risk assessment"),
    lon: float = Query(..., description="Longitude for regional risk assessment"),
    db: Session = Depends(get_db)
):
    """
    SDIRS Predictive Operations (Module 5): Suggestions to move units *before* the disaster hits.
    """
    try:
        prediction = await PredictionEngine.get_disaster_risks(lat, lon)
        suggestions = ResourceAllocationAI.suggest_prepositioning(db, prediction.risks)
        return {
            "status": "success",
            "region": {"lat": lat, "lon": lon},
            "suggestions": suggestions
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
