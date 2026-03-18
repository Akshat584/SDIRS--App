# SDIRS: Run Guide

This guide provides instructions on how to set up and run the **Smart Disaster Intelligence & Response System (SDIRS)** locally.

## 1. Prerequisites

Before starting, ensure you have the following installed:
- **Python 3.10+**
- **Node.js (v18+)** & **npm**
- **PostgreSQL** with **PostGIS** extension
- **Expo Go** app (optional, for mobile testing)

---

## 2. Database Setup

1.  **Start PostgreSQL** service.
2.  **Create a database** named `disaster_db`:
    ```sql
    CREATE DATABASE disaster_db;
    ```
3.  **Enable PostGIS** (The system will attempt this automatically, but ensure the extension is available in your Postgres installation):
    ```sql
    \c disaster_db;
    CREATE EXTENSION postgis;
    ```
4.  **Update Configuration**: Check `backend/.env` and ensure `DATABASE_URL` matches your local Postgres credentials.
    - Default: `postgresql://postgres:postgres@localhost:5432/disaster_db`

---

## 3. Backend Setup (FastAPI)

1.  **Navigate to backend directory**:
    ```bash
    cd backend
    ```
2.  **Create and activate a virtual environment**:
    ```bash
    python -m venv venv
    # Windows:
    venv\Scripts\activate
    # Linux/Mac:
    source venv/bin/activate
    ```
3.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
4.  **Initialize Database**:
    ```bash
    python init_db.py
    ```
5.  **Run the Server**:
    ```bash
    uvicorn main:sio_app --reload --host 0.0.0.0 --port 8000
    ```
    - API Docs: [http://localhost:8000/docs](http://localhost:8000/docs)
    - Root Status: [http://localhost:8000/](http://localhost:8000/)

---

## 4. Frontend Setup (React Command Center)

1.  **Navigate to frontend directory**:
    ```bash
    cd frontend
    ```
2.  **Install dependencies**:
    ```bash
    npm install
    ```
3.  **Run the Web App**:
    ```bash
    npm start
    ```
    - The dashboard will be available at [http://localhost:3000](http://localhost:3000)

---

## 5. Mobile App Setup (React Native / Expo)

1.  **Navigate to mobile-app directory**:
    ```bash
    cd mobile-app
    ```
2.  **Install dependencies**:
    ```bash
    npm install
    ```
3.  **Configure Environment**:
    - Open `mobile-app/.env`.
    - Set `EXPO_PUBLIC_SOCKET_URL` to your machine's local IP address (e.g., `http://192.168.1.10:8000`).
4.  **Run the App**:
    ```bash
    npx expo start
    ```
    - Use the **Expo Go** app on your phone to scan the QR code, or press `a` for Android emulator / `i` for iOS simulator.

---

## 6. Project Architecture & Ports
- **Backend API**: `8000`
- **Socket.io**: `8000` (Integrated with FastAPI)
- **Frontend Dashboard**: `3000`
- **Mobile Metro Bundler**: `8081`
