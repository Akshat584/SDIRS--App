# SDIRS: Debugging & Troubleshooting Guide

This guide covers common issues and debugging techniques for the SDIRS ecosystem.

## 1. Backend Debugging (FastAPI)

### Common Issues
- **Database Connection Failure**: 
    - Ensure PostgreSQL is running.
    - Check if the password in `.env` is correct.
    - Verify `disaster_db` exists.
- **PostGIS Not Found**:
    - Error: `type "geometry" does not exist`.
    - Fix: Run `CREATE EXTENSION postgis;` in your PostgreSQL console for `disaster_db`.
- **ImportErrors**:
    - Ensure you are inside the `venv`.
    - Run `pip install -r requirements.txt` again to ensure all packages (especially `psycopg2-binary` and `GeoAlchemy2`) are installed.

### Debugging Tools
- **Interactive Docs**: Go to `http://localhost:8000/docs` to test API endpoints directly.
- **Uvicorn Logs**: The terminal running `uvicorn` shows real-time requests and errors.
- **Print/Logging**: Use `logging.info()` or `print()` in the code to trace data flow.

---

## 2. Frontend Debugging (React)

### Common Issues
- **Empty Map / Data Not Loading**:
    - Check Browser Console (`F12` -> `Console`).
    - Verify the Backend is running on `localhost:8000`.
    - Check `Network` tab for failed `GET /api/incidents` requests.
- **Socket Disconnected**:
    - The UI top bar should show `WEBSOCKETS: CONNECTED`.
    - If `DISCONNECTED`, check if the backend `sio_app` is running.

### Debugging Tools
- **React Developer Tools**: Inspect component state (like `incidents` or `responders`).
- **Network Tab**: Verify the `ws://` (WebSocket) connection status and messages.

---

## 3. Mobile App Debugging (Expo)

### Common Issues
- **Network Error / Backend Unreachable**:
    - Physical devices **cannot** connect to `localhost`.
    - You MUST use your machine's **Local IP address** in `mobile-app/.env` (e.g., `192.168.x.x`).
    - Ensure your phone and computer are on the same Wi-Fi network.
- **Metro Bundler Hangs**:
    - Run `npx expo start --clear` to reset the cache.

### Debugging Tools
- **Expo Console**: Logs are visible in the terminal where you ran `npx expo start`.
- **Remote Debugging**: Press `j` in the terminal to open Chrome DevTools for the mobile app.

---

## 4. Database Debugging

- **SQL Console**: Use `psql -U postgres -d disaster_db` or **pgAdmin** to inspect tables.
- **Table Verification**:
    - `SELECT * FROM incidents;`
    - `SELECT * FROM users;`
- **Geometry Checks**:
    - If locations aren't showing on the map, ensure the `location` column is populated with valid WKB (Well-Known Binary) data.

---

## 5. Socket.io Event Tracing
To see real-time events across the system:
1. Open the Backend terminal.
2. Observe logs like `SDIRS Client connected: <sid>`.
3. Check for events like `Incident update: { ... }` which trigger UI refreshes.
