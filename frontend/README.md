# SDIRS Command Center: Real-Time Visual Intelligence Dashboard

The SDIRS Frontend is a sophisticated React-based "Command Center" designed for emergency dispatchers and government officials. It provides a live, unified view of all disaster-related data, allowing for rapid decision-making.

## 🌟 Key Features

- **Live Tactical Map:** Built with **Leaflet**, displaying real-time incident markers, responder locations, and active drone paths.
- **AI Risk Forecasting:** A sidebar that streams predictions from the backend AI engine, highlighting zones with high probability of disasters.
- **Incident Feed:** Real-time triage of incoming citizen reports, categorized by AI-predicted severity (Critical, High, Medium, Low).
- **Integrated Communication:** A WebSocket-powered chat and broadcast system for direct coordination with field units.
- **Digital Twin (3D):** A specialized view for 3D visualization of urban environments and disaster impact.
- **AI Intelligence Analytics:** A comprehensive dashboard using **Recharts** to visualize system performance, resource utilization, and incident trends.

## 🛠 Technology Stack

- **Framework:** React.js (v18)
- **Mapping:** React-Leaflet / Leaflet.js
- **Icons:** Lucide-React
- **Real-Time:** Socket.io-client
- **Charts:** Recharts
- **Styling:** Vanilla CSS (Cyber-Grid Aesthetic)
- **API Client:** Axios

## 📂 UI Components

- `App.js`: Main layout with conditional rendering for Command, Twin, and Intelligence views.
- `components/DigitalTwin3D.js`: Handles 3D rendering logic.
- `App.css`: Defines the unique dark-mode, high-contrast SDIRS theme.

## 🚀 Getting Started

1. **Install:** Run `npm install`.
2. **Run:** Run `npm start`.
3. **Connect:** Ensure the backend is running at `http://localhost:8000` to receive real-time updates.
