# Backend Deep Dive: SDIRS Technical Architecture & Logic

This document provides a detailed technical breakdown of the SDIRS Backend, explaining the logic and algorithms behind its core modules.

---

## 1. AI Prediction Engine (Module 1)
**Logic:** The system uses a **Random Forest Classifier** trained on historical disaster data.
- **Inputs:** Temperature, Rainfall, Population Density, and real-time IoT values (Water Level, Seismic Magnitude, Smoke Concentration).
- **Processing:** The engine performs a weighted analysis. For example, even if the ML model predicts a "medium" risk, a high "Water Level" reading from an IoT sensor will dynamically upgrade the status to "Critical Flood Risk."
- **Output:** A `PredictionResponse` containing disaster types, probabilities (0-1), and actionable recommendations.

## 2. AI Incident Verification (Module 3)
**Logic:** To prevent false reports, SDIRS uses a multi-layered verification strategy:
- **NLP Triage:** Uses a BERT-based model (`sdirs-bert-uncased`) to analyze the description of an incident and assign a predicted severity and category.
- **Cross-Source Validation:** Matches citizen reports against USGS Earthquake feeds, OpenWeatherMap alerts, and social media trends (mocked via `social_media_service`).
- **Confidence Scoring:** Assigns a confidence value (0-100%). Reports with >80% confidence are automatically marked as `verified`.

## 3. Smart Resource Allocation (Module 5)
**Logic:** This is an **Optimization Problem** solved via a custom scoring algorithm.
- **Spatial Query:** Uses PostGIS `ST_DWithin` to find resources within a 5-10km radius of an incident.
- **Scoring Formula:**
    - `Proximity Score (50 pts)`: Closer resources get higher points.
    - `Workload Score (30 pts)`: Resources with available capacity/lower workload are prioritized.
    - `Skill Match (25 pts)`: Matches incident type (e.g., Fire) with resource skills (e.g., Firefighter).
    - `Equipment Check (-40 penalty)`: Resources with low fuel or malfunctioning equipment are deprioritized.
- **Auto-Dispatch:** The system automatically creates `Allocation` entries for the top-scoring resources.

## 4. Hazard-Aware Routing (Module 6)
**Logic:** Combines traditional navigation with dynamic disaster data.
- **Base Layer:** Fetches routes from **Google Maps Directions API**.
- **SDIRS Overlay:** Iterates through every coordinate in the Google Maps route and performs a distance check against **Active Hazards** (Fire zones, Floods, Roadblocks) in the SDIRS database.
- **Hazard Warning:** If the route passes within 200m of a hazard, the system injects a `CRITICAL_WARNING` and details of the hazard into the navigation response.

## 5. IoT Sensor Fusion & MQTT Simulator
**Logic:** Mimics a real-world sensor network.
- **Background Task:** A persistent `asyncio` loop generates synthetic data for multiple sensor types (Seismic, Smoke, Water).
- **Ground Truth Adjustment:** Provides the "Ground Truth" for the Prediction Engine, ensuring that AI predictions are grounded in real-time physical measurements.

## 6. Real-Time WebSocket Orchestration
**Logic:** Integrated via `python-socketio` mounted as an ASGI app.
- **Event-Driven:** Instead of polling, the backend *pushes* updates (e.g., `incident_update`, `prediction_alert`) to all connected clients.
- **State Sync:** Ensures the Command Center map and Mobile App alerts are perfectly synchronized without reloading.
