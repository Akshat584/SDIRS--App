import asyncio
from app.services.prediction_engine import PredictionEngine
from app.models.heatmap import HeatmapPoint

async def test_heatmap_generation():
    print("--- Testing Heatmap Risk Data Generation (Module 8) ---")
    
    # Mock center: Lucknow
    lat, lon = 26.8467, 80.9462
    
    # Simulate risk points generation
    prediction = await PredictionEngine.get_disaster_risks(lat, lon)
    
    heatmap_points = []
    for risk in prediction.risks:
        point = HeatmapPoint(
            lat=lat,
            lon=lon,
            intensity=risk.probability,
            type='prediction',
            label=f"{risk.disaster_type} Risk",
            radius=800 if risk.alert_level == 'critical' else 600
        )
        heatmap_points.append(point)
        print(f"Generated Heatmap Point: {point.label} - Intensity: {point.intensity}")

    assert len(heatmap_points) > 0
    print("\nHeatmap Generation Test Passed!")

if __name__ == "__main__":
    asyncio.run(test_heatmap_generation())
