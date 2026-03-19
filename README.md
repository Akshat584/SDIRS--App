# 🌐 SDIRS: Smart Disaster Intelligence & Response System

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React Native](https://img.shields.io/badge/Mobile-React_Native-61DAFB?style=for-the-badge&logo=react&logoColor=black)](https://reactnative.dev/)
[![AI/ML](https://img.shields.io/badge/AI%2FML-TensorFlow%20%7C%20Scikit--Learn-FF6F00?style=for-the-badge&logo=tensorflow&logoColor=white)](https://www.tensorflow.org/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostGIS-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://postgis.net/)

> **Architected & Developed by [Akshat Pal](https://github.com/AkshatPal)** 🚀
> (Core Backend & Mobile Infrastructure)

SDIRS is an advanced, multi-layered ecosystem designed to transform disaster management from a reactive manual process into a proactive, **AI-driven autonomous coordination platform**. By integrating real-time IoT data, Computer Vision, and predictive modeling, SDIRS enables responders to save lives with surgical precision.

---

## 🏗️ System Architecture

SDIRS follows a high-performance micro-service inspired architecture designed for extreme reliability during critical events.

- **Mobile App (Edge):** Citizen reporting and responder navigation (React Native/Expo).
- **AI Gateway (Core):** High-speed asynchronous processing (FastAPI/Python 3.14).
- **Intelligence Layer:** Predictive models and Computer Vision (TensorFlow, YOLO, Scikit-Learn).
- **Real-Time Layer:** Bi-directional event orchestration (Socket.io).
- **Spatial Intelligence:** Geo-spatial querying and routing (PostGIS + Google Maps API).

---

## 🧠 Core Modules (The 10 Pillars)

### 1. 🔮 Disaster Prediction Engine
Uses Random Forest models trained on historical and OpenWeatherMap data to predict "Risk Probabilities." Even if ML predicts low risk, high IoT sensor triggers (Water/Seismic) can dynamically elevate alert levels.

### 2. 📱 Citizen Reporting Network
A streamlined reporting interface supporting GPS tagging, description, and high-res image uploads with UUID masking for security.

### 3. 👁️ AI Incident Verification
To eliminate false reports, this module uses **YOLO/OpenCV** for visual hazard detection and a **BERT-based NLP model** to categorize severity from text descriptions.

### 4. 🛰️ Emergency Command Center
A live, centralized dashboard (React + Mapbox GL) that visualizes active incidents, responder movements, and drone feeds in real-time.

### 5. 🚒 Smart Resource Allocation AI
An optimization engine that solves dispatching using a multi-factor scoring algorithm:
`Score = (Proximity × 0.5) + (Workload × 0.3) + (SkillMatch × 0.2) - (EquipmentPenalty)`

### 6. 🛣️ Hazard-Aware Routing
Integrates with Google Maps API but injects an **SDIRS Hazard Layer**. If a route passes within 200m of an active fire or flood, the system recalculates and issues a `CRITICAL_WARNING`.

### 7. 🚁 Drone Monitoring System
Supports live WebRTC/RTSP stream ingestion for aerial reconnaissance, providing a "eye-in-the-sky" view for floods and search-and-rescue.

### 8. 🗺️ Dynamic Disaster Heatmaps
Uses `turf.js` and Mapbox to generate live heatmaps of risk zones, helping authorities prioritize evacuation routes and resource staging.

### 9. 💬 Emergency Communication
A secure, low-latency team chat powered by WebSockets. Features "Command Broadcasts" that override all responder screens for mission-critical orders.

### 10. 📊 Disaster Analytics
Aggregates allocation data and response times into actionable D3.js/Recharts visualizations to improve future preparedness strategies.

---

## 🛠️ Tech Stack

### **Backend (Developed by Akshat Pal)**
- **Framework:** FastAPI (Asynchronous Python)
- **Database:** PostgreSQL + PostGIS (Spatial Indexing)
- **Real-Time:** Socket.io (WebSockets)
- **ML/AI:** Scikit-Learn, TensorFlow, YOLO, BERT (NLP)
- **Auth:** JWT + Role-Based Access Control (RBAC)

### **Mobile App (Developed by Akshat Pal)**
- **Framework:** React Native + Expo (TypeScript)
- **Navigation:** Expo Router
- **Backend-as-a-Service:** Supabase (for supplemental data/auth)
- **Mapping:** React Native Maps + Expo Location
- **Communication:** Socket.io-client

### **Frontend (Command Center)**
- **Framework:** React.js
- **Visualization:** Mapbox GL, Recharts

---

## 🚀 Getting Started

### Backend Setup
1. `cd backend`
2. `python -m venv venv`
3. `source venv/bin/activate` (or `venv\Scripts\activate` on Windows)
4. `pip install -r requirements.txt`
5. `uvicorn main:app --reload`

### Mobile App Setup
1. `cd mobile-app`
2. `npm install`
3. `npx expo start`

---

## 📄 License & Contribution
This project is built as a state-of-the-art response to modern disaster challenges. For technical inquiries or collaboration, contact **Akshat Pal**.

---
*Predict. Respond. Recover. SDIRS.*
