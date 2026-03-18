# Priority Task Workflow (SDIRS)

This document tracks the implementation progress of the AI-Powered Smart Disaster Intelligence & Response System (SDIRS).

## Status Legend
- [x] Completed
- [ ] To Do
- [▶] In Progress
- [⏸] Blocked

---

## Phase 1: Foundation & Restructuring
- [x] Create `docs/PRIORITY_TASKS.md` and move existing task tracking there.
- [x] Reorganize the root directory to strictly follow the `backend`, `frontend`, `mobile-app` structure.
- [x] Update `README.md` to reflect the new SDIRS vision and architecture.
- [x] Update `ROADMAP.md` to align with the SDIRS modules.
- [x] Clean up redundant legacy files (Node.js in backend, root HTML, etc.).
- [x] Update and install backend and mobile dependencies.
- [x] Align the file directory structure to the SDIRS architecture (Core, ML Pipeline, Frontend scaffold).

## Phase 2: Core Backend Services & DB
- [x] Define the PostgreSQL schema for Incidents, Resources, Users, and Analytics.
- [x] Implement the Citizen Reporting API (receiving photos, GPS, descriptions).
- [x] Set up the basic WebSockets infrastructure for the Command Center.

## Phase 3: AI Modules (The "Brains")
- [x] Develop the Disaster Prediction Engine (combining weather and historical data).
- [x] Integrate the AI Incident Verification System (image analysis via YOLO/TensorFlow).
- [x] Build the Smart Resource Allocation AI (distance + severity + workload).

## Phase 4: Command Center & Real-Time (Frontend)
- [x] Build the Real-Time Emergency Command Center dashboard map.
- [x] Implement Disaster Heatmap & Risk Visualization.
- [x] Create the Analytics & Intelligence Dashboard.

## Phase 5: Mobile Apps & Edge (Citizen/Responder)
- [x] Implement Traffic-Aware Route Optimization in the responder app.
- [x] Build the Emergency Communication System (chat/broadcasts).
- [x] Develop the Citizen Reporting interface in the mobile app.

## Phase 6: Initial Integrations
- [x] Drone Monitoring System integration (video stream placeholders/endpoints).

---

## Phase 7: Resilient & Omni-Channel Alerting (Critical Response)
- [x] **Spatial Alert Query:** Implement PostGIS `ST_DWithin` logic to find all responders/ambulances within 5km of verified incidents.
- [x] **Omni-Channel Trigger:**
    - [x] Real-time WebSocket broadcast to active responder dashboards.
    - [x] Firebase Cloud Messaging (FCM) push notifications for mobile devices. (Mocked)
    - [x] SMS/Voice alerts via Twilio API for senior officials (Authority API). (Mocked)
- [x] **Edge AI Verification:** Deploy TensorFlow Lite to the mobile app for instant on-device image verification (zero-bandwidth triage).
- [x] **Offline Resilience:** Implement BLE (Bluetooth Low Energy) mesh networking for P2P SOS messaging when networks fail.

## Phase 8: Advanced Proactive Detection & Prediction
- [x] **IoT Sensor Fusion:** Integrate real-time seismic, water level, and smoke sensors via MQTT for ground-truth data. (Simulated MQTT + In-memory fusion)
- [x] **Advanced ML Prediction Engine:** Evolve models to analyze weather + IoT + historical frequency for high-precision risk probabilities. (Random Forest Classifier + IoT Features)
- [x] **Real NLP Sentiment Analysis:** Replace mock scraper with real Twitter/Reddit API pipeline + BERT model for incident classification. (Mocked stream + BERT Triage Model)
- [x] **Predictive Resource Pre-Positioning:** AI suggestions to move units *before* the disaster hits based on risk levels.

## Phase 9: Autonomous Coordination & Operations
- [x] **Smart Resource AI (V2):** Optimize allocation based on workload, specialized skills, and responder equipment status.
- [x] **Autonomous Drone SAR:** Implement autonomous "S-pattern" search flight paths with "Human in Distress" visual detection.
- [x] **Digital Twin / 3D Visualization:** Implement Three.js/Cesium 3D city view for flood and terrain analysis in the command center. (Three.js Procedural City + Flood Sim)
- [x] **Hazard-Aware Routing:** Integrate live road closures and flood reports into the responder navigation algorithm. (Google Maps + SDIRS Hazard Cross-check)

## Phase 10: Community-Driven Recovery & Integrity
- [ ] **C2C (Citizen-to-Citizen) Mutual Aid:** "Neighbor-in-Need" module for local resource sharing (generators, tools, medical kits).
- [ ] **Blockchain for Resource Integrity:** Log distribution of critical supplies on a transparent ledger to ensure accountability.
- [ ] **AR Responder Navigation:** AR overlay of fire hydrants, gas lines, and safe paths on the responder's camera feed.

---

## AI/ML Training & Deployment Pipeline
1.  **Data Prep:** Extract SQL logs + Weather API + IoT logs into labeled CSV datasets.
2.  **Training (`ml_pipeline/train.py`):**
    *   `Scikit-learn` (Random Forest) for Severity/Resource prediction.
    *   `TensorFlow` (YOLOv8/EfficientNet) for Image Verification.
3.  **Deployment:** Export as `.joblib` or `.tflite`. FastAPI loads models at startup for real-time inference.
