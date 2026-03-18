# SDIRS Backend: AI-Powered Smart Disaster Intelligence & Response System

The SDIRS Backend is a high-performance, asynchronous Python-based ecosystem built with **FastAPI**. it serves as the "brain" of the disaster management platform, integrating real-time data from IoT sensors, weather feeds, and social media to provide predictive analytics and coordinate emergency responses.

## 🚀 Core Functionalities

- **Disaster Prediction Engine (Module 1):** Uses a Random Forest ML model to analyze weather, population density, and IoT data to predict flood, fire, and seismic risks.
- **Incident Management (Module 2 & 3):** Handles citizen reports, performs AI-driven triage (BERT-based NLP), and verifies authenticity using cross-source data.
- **Real-Time Command & Control (Module 4):** Powered by **Socket.io** for bi-directional communication with the Command Center and Mobile Apps.
- **Smart Resource Allocation AI (Module 5):** An optimization engine that assigns responders based on distance (PostGIS), workload, specialized skills, and equipment status.
- **Hazard-Aware Routing (Module 6):** Integrates Google Maps API with live disaster data to provide emergency vehicles with routes that avoid active hazards.
- **Drone Monitoring (Module 7):** Manages a virtual fleet of drones for aerial surveillance and SAR missions.
- **IoT Sensor Fusion:** A background MQTT simulator that mimics live data from water level, seismic, and smoke sensors.

## 🛠 Technology Stack

- **Framework:** FastAPI (Python 3.10+)
- **Real-Time:** Python-Socketio (ASGI)
- **Database:** PostgreSQL + PostGIS (Spatial Data)
- **ORM:** SQLAlchemy + GeoAlchemy2
- **AI/ML:** Scikit-Learn (Risk Prediction), BERT (NLP Triage), Joblib
- **Asynchronous Tasking:** Python `asyncio`
- **GIS Logic:** Shapely, GeoAlchemy2

## 📂 Project Structure

- `app/api/`: RESTful endpoints for incidents, drones, analytics, etc.
- `app/core/`: Configuration, security (JWT), and WebSocket management.
- `app/db/`: Database models and PostGIS schemas.
- `app/models/`: Pydantic schemas for data validation.
- `app/services/`: The core business logic (AI engines, routing, IoT fusion).
- `main.py`: Entry point for the FastAPI + Socket.io application.

## 🔧 Installation & Setup

1. **Environment:** Create a venv and run `pip install -r requirements.txt`.
2. **Database:** Ensure PostgreSQL with PostGIS is running and create `disaster_db`.
3. **Initialization:** Run `python init_db.py` to create tables and enable spatial extensions.
4. **Execution:**
   ```bash
   uvicorn main:sio_app --reload --host 0.0.0.0 --port 8000
   ```
