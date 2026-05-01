# SDIRS Quick Start Guide

## Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Expo Go app (for mobile testing)

## Run Everything (3 Terminals)

### Terminal 1: Backend
```bash
cd backend
pip install -r requirements.txt
python init_db.py
uvicorn main:sio_app --reload --host 0.0.0.0 --port 8000
```

### Terminal 2: Frontend
```bash
cd frontend
npm install
npm start
```

### Terminal 3: Mobile
```bash
cd mobile-app
npm install
# Update .env with your IP
npx expo start
```

## Test Flow
1. Open http://localhost:3000 (web dashboard)
2. Scan QR code with Expo Go (mobile app)
3. Report incident on mobile
4. See it appear on web dashboard instantly

