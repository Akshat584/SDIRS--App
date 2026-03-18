# SDIRS Advanced Priority Workflow (Phase 2)

This document outlines the next evolution of the Smart Disaster Intelligence & Response System (SDIRS), transitioning from a reactive tool to a proactive, resilient, and autonomous ecosystem.

---

## Phase A: Proactive Detection & Intelligence (Before Disaster)

The goal is to move from "responding to reports" to "predicting risks."

1.  **IoT Sensor Fusion (MQTT Integration)**
    *   **Action:** Integrate real-time seismic, water level, and smoke sensors via MQTT.
    *   **Value:** Provides "Ground Truth" data that is more reliable than manual reporting.
2.  **AI Prediction Engine (Advanced Modeling)**
    *   **Action:** Implement Random Forest/XGBoost models in `backend/ml_pipeline/` that analyze weather patterns, historical data, and IoT streams.
    *   **Output:** Predict "Risk Probability" for specific GPS zones.
3.  **Digital Twin & 3D Visualization**
    *   **Action:** Implement a Three.js or Cesium-based 3D map in the Command Center.
    *   **Value:** Visualize flood levels relative to building heights and terrain for better evacuation planning.

---

## Phase B: Resilient Reporting & Omni-Channel Alerting (During Disaster)

Ensuring information flows even when the infrastructure is failing.

1.  **Edge-AI Verification (On-Device Inference)**
    *   **Action:** Deploy TensorFlow Lite models to the mobile app for instant image verification (Fire/Flood detection) without needing a server connection.
2.  **Omni-Channel Alert System**
    *   **Action:** Implement a multi-tier alert trigger upon incident verification:
        *   **Spatial Query:** Find all responders/ambulances within 5km using PostGIS `ST_DWithin`.
        *   **Real-Time:** WebSocket broadcast to active responder dashboards.
        *   **Mobile:** Firebase Cloud Messaging (FCM) push notifications for offline devices.
        *   **Authorities:** SMS/Voice alerts via Twilio API for senior government officials.
3.  **Resilient Communication (Offline-First)**
    *   **Action:** Implement BLE (Bluetooth Low Energy) mesh networking and Wi-Fi Direct for Peer-to-Peer (P2P) SOS messaging.
    *   **Action:** Implement Offline Mapping (Mapbox tile caching) to ensure navigation works without cellular data.

---

## Phase C: Autonomous Coordination & Optimization (Action)

Maximizing the efficiency of the response through AI and automation.

1.  **Smart Resource Allocation AI (V2)**
    *   **Action:** Evolve the allocation logic to consider not just distance, but responder workload, specialized skills (e.g., medical vs. fire), and current fuel/battery levels.
2.  **Traffic-Aware & Hazard-Aware Routing**
    *   **Action:** Integrate live citizen reports (e.g., "Road Blocked") directly into the responder's A* navigation algorithm.
3.  **Autonomous Drone Search & Rescue (SAR)**
    *   **Action:** Implement autonomous flight patterns (S-pattern) with AI-powered "Human in Distress" detection from live video feeds.

---

## Phase D: Community-Driven Recovery & Transparency

Empowering citizens and ensuring resource integrity.

1.  **C2C (Citizen-to-Citizen) Mutual Aid**
    *   **Action:** A "Neighbor-in-Need" module where users can request or offer tools (generators, medical kits) and assistance locally.
2.  **AR Responder Navigation**
    *   **Action:** Overlay fire hydrants, gas lines, and safe paths over the responder's camera feed using Augmented Reality (Expo AR).
3.  **Blockchain for Resource Integrity**
    *   **Action:** Log the distribution of critical supplies (food, water, medicine) on a transparent ledger to prevent corruption and ensure accountability.

---

## AI/ML Training & Deployment Pipeline

To implement the "Brains" of Phase 2, follow this standardized pipeline:

### 1. Data Preparation
*   Extract historical incident logs from the database.
*   Merge with historical weather data (OpenWeatherMap API) and IoT sensor logs.
*   Label data by severity (0: Low, 1: Med, 2: High, 3: Critical).

### 2. Model Training (`backend/ml_pipeline/train.py`)
```python
import joblib
from sklearn.ensemble import RandomForestClassifier

# Load structured history
X_train, y_train = load_disaster_features()

# Train Severity Model
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# Save for API use
joblib.dump(model, 'backend/ml_pipeline/models/severity_model_v2.joblib')
```

### 3. Production Deployment
*   **Load:** The FastAPI backend loads the model at startup.
*   **Predict:** When a new sensor reading or report arrives, the API calls `model.predict()` to instantly update the risk heatmap and trigger the Omni-Channel Alert system.
