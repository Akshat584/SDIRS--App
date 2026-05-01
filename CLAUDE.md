# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SDIRS (Smart Disaster Intelligence & Response System) is a comprehensive AI-powered disaster management platform with 10 core modules covering prediction, response coordination, and analytics. The system consists of:

- **Backend**: FastAPI (Python) with WebSocket real-time communication
- **Frontend**: React.js command center dashboard with map visualization
- **Mobile App**: React Native (Expo) for citizen/responder reporting
- **Database**: PostgreSQL with PostGIS (spatial queries), SQLite for development

## Quick Start

### Running the Full Stack (3 Terminals)

**Terminal 1 - Backend:**

```bash
cd backend
python init_db.py           # Initialize database
python -m uvicorn main:sio_app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**

```bash
cd frontend
npm install
npm start  # Runs on http://localhost:3000
```

**Terminal 3 - Mobile:**

```bash
cd mobile-app
npm install
npx expo start  # Runs on http://localhost:8081
```

### Development Setup

**Backend Dependencies:**

```bash
cd backend
pip install -r requirements.txt
```

**Frontend Dependencies:**

```bash
cd frontend
npm install
```

**Mobile Dependencies:**

```bash
cd mobile-app
npm install
npx expo install --fix  # Fix dependency compatibility
```

## Architecture & Code Structure

### Backend (`backend/`)

FastAPI application organized into modular microservices:

- **`app/api/`** - API route handlers organized by module:
  - `incidents.py` - Citizen reporting (Module 2)
  - `predictions.py` - Disaster prediction engine (Module 1)
  - `earthquakes.py`, `weather_alerts.py` - Data ingestion (Module 1)
  - `social_media.py` - AI verification (Module 3)
  - `heatmap.py` - Risk visualization (Module 8)
  - `analytics.py` - Intelligence dashboard (Module 10)
  - `routing.py` - Route optimization (Module 6)
  - `messages.py` - Communication system (Module 9)
  - `drones.py` - Drone monitoring (Module 7)

- **`app/core/`** - Core infrastructure:
  - `config.py` - Configuration management (Pydantic Settings)
  - `websockets.py` - Socket.IO server setup
  - `security.py` - Authentication/JWT

- **`app/db/`** - Database layer:
  - `database.py` - SQLAlchemy setup
  - `incidents.py`, `safe_zones.py` - Model definitions
  - `schemas.py` - Pydantic schemas

**Database:**

- Uses SQLite by default (`sdirs_dev.sqlite`, `disaster_db.sqlite`)
- PostgreSQL with PostGIS for production
- Initialize with `python init_db.py` (creates tables, loads sample data)

**Key Configuration:**

- Environment files: `backend/.env` (dev), `.env.production`
- CORS configured for mobile/web communication
- WebSocket server integrated with FastAPI via `socketio.ASGIApp`

### Frontend (`frontend/`)

React command center dashboard:

- **`src/App.js`** - Main dashboard with real-time incident feed, map, and analytics
- **`src/components/`** - UI components including `DigitalTwin3D`
- Real-time updates via Socket.IO
- Map visualization using React-Leaflet (OpenStreetMap/CartoDB)
- Three views: Command Map, Digital Twin, AI Intelligence

**Key Features:**

- Live incident tracking with severity badges
- Interactive map with incident markers, heatmaps, drones, responders
- Communication panel for broadcasts
- Real-time statistics dashboard

### Mobile App (`mobile-app/`)

React Native (Expo) application for citizens and responders:

- **`app/(tabs)/`** - Main navigation screens:
  - `index.tsx` - Dashboard with alerts
  - `map.tsx` - Interactive map view
  - `alerts.tsx` - Alert notifications
  - `report.tsx` - Incident reporting with photo upload
  - `messages.tsx` - Communication

- **`services/`** - API and external service integrations:
  - `apiConfig.ts` - **Centralized API configuration** (created to fix hardcoded URLs)
  - `socketService.ts` - WebSocket communication
  - `authService.ts` - Authentication (Supabase)
  - `heatmapService.ts` - Risk visualization data
  - `routingService.ts` - Route optimization
  - `bleService.ts` - BLE mesh networking for offline SOS
  - `supabaseClient.ts` - Backend-as-a-Service integration

- **`components/ErrorBoundary.tsx`** - Error handling component (added to prevent crashes)
- **`utils/validation.ts`** - Input validation utilities

**Key Improvements (see MOBILE_APP_IMPROVEMENTS.md):**

- Fixed TypeScript compilation errors
- Resolved memory leaks in BLE service
- Enhanced error handling across all services
- Centralized API configuration
- Added timeout handling (10-20s for various requests)

## Common Development Tasks

### Running Tests

**Backend:**

```bash
cd backend
pytest  # All tests
pytest tests/test_incidents.py -v  # Specific test file
```

**Frontend:**

```bash
cd frontend
npm test
```

**Mobile:**

```bash
cd mobile-app
npm test
# Type checking
npx tsc --noEmit
# Linting
npm run lint
# Expo doctor
npx expo-doctor
```

### Database Operations

**Initialize/Reset Database:**

```bash
cd backend
python init_db.py  # Creates tables and sample data
python check_db.py  # Verify database state
```

**Alembic Migrations:**

```bash
cd backend
alembic upgrade head  # Apply migrations
alembic revision --autogenerate -m "Description"  # Create migration
```

### Code Quality

**Backend:**

```bash
cd backend
python -m flake8 app/
python -m black app/
python -m isort app/
```

**Frontend:**

```bash
cd frontend
npm run lint
npm run format  # If configured
```

**Mobile:**

```bash
cd mobile-app
npm run lint
npx expo install --fix  # Fix dependency issues
npx expo-doctor  # Diagnose problems
```

### Building & Deployment

**Docker Deployment:**

```bash
./deploy.sh  # Automated full-stack deployment
./deploy.sh dev  # Development mode
./deploy.sh prod  # Production mode
```

**Individual Builds:**

```bash
# Backend Docker
cd backend
docker build -t sdirs-backend .

# Frontend Build
cd frontend
npm run build

# Mobile App Build (Expo)
cd mobile-app
eas build --platform android  # Or ios
```

## API Endpoints

### Core Endpoints

**Incidents:**

- `GET /api/incidents` - List all incidents
- `POST /api/incidents` - Create incident report
- `GET /api/incidents/{id}` - Get incident details
- `PATCH /api/incidents/{id}` - Update incident status

**Predictions & Data:**

- `GET /api/predictions` - Get disaster predictions
- `GET /api/earthquakes` - Latest earthquake data
- `GET /api/weather_alerts` - Weather alerts
- `GET /api/heatmap` - Risk heatmap data

**Analytics:**

- `GET /api/dashboard-metrics` - Command center metrics
- `GET /api/analytics` - Detailed analytics

**Real-time:**

- WebSocket namespace `/` - Incident updates, location tracking, messages

**Special Endpoints:**

- `GET /api/red-alert` - Check red alert status
- `GET /api/verify-data` - AI verification cross-check
- `GET /api/drones/fleet` - Drone fleet status

## Environment Configuration

**Root `.env.example`:**

- Shared environment variables template

**Backend `.env`:**

- `DATABASE_URL` - PostgreSQL connection (default: `postgresql://postgres:postgres@localhost:5432/disaster_db`)
- `ALLOWED_ORIGINS` - CORS origins (comma-separated)
- `ENVIRONMENT` - development/production
- Upload directories and API keys

**Mobile `.env`:**

- `EXPO_PUBLIC_SOCKET_URL` - Backend WebSocket URL (**must be your local IP, not localhost**)
- Supabase configuration
- API endpoints

**⚠️ Important:** Mobile app requires your computer's local IP address in `EXPO_PUBLIC_SOCKET_URL` (e.g., `http://192.168.1.100:8000`). Using `localhost` won't work on physical devices.

## Development Best Practices

### Backend

- Use Pydantic models for request/response validation
- Implement proper error handling with HTTPException
- Use async/await for I/O operations
- Organize business logic in `app/services/`
- WebSocket events for real-time updates

### Frontend

- Keep API calls in dedicated service files
- Use React hooks for state management
- Implement proper cleanup in useEffect
- Handle loading and error states

### Mobile

- **Use centralized API config** (`services/apiConfig.ts`)
- Add timeout handling to all async operations (10-20s recommended)
- Implement proper error boundaries
- Clean up intervals and listeners to prevent memory leaks
- Use TypeScript strict mode
- Follow Expo best practices

## Key Files & Documentation

**Project Documentation:**

- `README.md` - Project overview and architecture
- `QUICKSTART.md` - Fast setup guide
- `RUN_GUIDE.md` - Detailed setup instructions
- `MOBILE_APP_IMPROVEMENTS.md` - Recent code quality improvements
- `docs/PRIORITY_TASKS.md` - Development roadmap and progress
- `task.md` - Full deployment and development plan

**Configuration:**

- `docker-compose.yml` - Production Docker setup
- `docker-compose.dev.yml` - Development Docker setup
- `deploy.sh` - Automated deployment script
- `.env.example` - Environment template

**Testing & Quality:**

- Backend tests in `backend/tests/`
- TypeScript configuration: `tsconfig.json` (mobile)
- ESLint configuration: `eslint.config.js` (mobile)

## Known Issues & Solutions

**Mobile App Network Errors:**

- **Issue**: `AxiosError: Network Error` on physical devices
- **Solution**: Update `EXPO_PUBLIC_SOCKET_URL` in `mobile-app/.env` to your local IP (not `localhost`)
- **Also check**: Search codebase for hardcoded URLs and replace with config

**Database Connection Issues:**

- **Issue**: PostgreSQL connection fails
- **Solution**: Ensure PostgreSQL is running, database exists, credentials correct
- **Alternative**: Use SQLite (default in development)

**Port Conflicts:**

- Backend: `8000` (Uvicorn)
- Frontend: `3000` (React)
- Mobile: `8081` (Metro bundler)
- If ports in use, modify in respective config files

## System Architecture (High-Level)

```
┌─────────────────────────────────────────────────────────┐
│                     Mobile App (React Native)            │
│  Citizens/Responders report incidents, receive alerts   │
└─────────────┬───────────────────────────────────────────┘
              │ HTTP/WebSocket
┌─────────────▼───────────────────────────────────────────┐
│              Backend API (FastAPI + Socket.IO)          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ Incidents   │  │ Predictions │  │ Analytics   │     │
│  │ Module 2    │  │ Module 1    │  │ Module 10   │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ Verification│  │ Heatmap     │  │ Routing     │     │
│  │ Module 3    │  │ Module 8    │  │ Module 6    │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
│  ┌─────────────┐  ┌─────────────┐                      │
│  │ Drones      │  │ Messages    │                      │
│  │ Module 7    │  │ Module 9    │                      │
│  └─────────────┘  └─────────────┘                      │
└─────────────┬───────────────────────────────────────────┘
              │
    ┌─────────┴─────────┐
    │                   │
┌───▼────┐        ┌────▼────┐
│ Frontend│        │Database │
│(React) │        │PostgreSQL│
│Dashboard│        │+ PostGIS │
└────────┘        └─────────┘
```

## Tips for Development

1. **Start with the mobile app** - It's production-ready with recent quality improvements (see MOBILE_APP_IMPROVEMENTS.md)
2. **Use the WebSocket events** - Real-time features depend on proper WebSocket setup
3. **Database initialization** - Run `python init_db.py` after pulling changes
4. **Check PRIORITY_TASKS.md** - Shows what's been completed and what's next
5. **Environment variables** - Keep secrets in `.env` files, never commit them
6. **Mobile testing** - Use Expo Go app for quick testing, physical device for network testing
7. **API testing** - Use FastAPI docs at http://localhost:8000/docs
8. **Map data** - Uses OpenStreetMap and CartoDB, no API keys required

## Support Resources

- **FastAPI**: https://fastapi.tiangolo.com/
- **React Leaflet**: https://react-leaflet.js.org/
- **Expo**: https://docs.expo.dev/
- **Socket.IO**: https://socket.io/docs/
- **PostGIS**: https://postgis.net/documentation/
