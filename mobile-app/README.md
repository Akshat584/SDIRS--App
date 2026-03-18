# SDIRS Mobile: Citizen Reporting & Responder Coordination

The SDIRS Mobile App is a cross-platform application built with **React Native (Expo)**. It serves two primary audiences: Citizens (reporting disasters) and Responders (receiving dispatches and sharing live locations).

## 📱 Features

- **Quick Incident Reporting:** Citizens can report disasters with GPS coordinates, photos, and descriptions.
- **AI Assistance:** Lightweight local AI logic for verifying reports before submission.
- **Live GPS Tracking:** Responders share their real-time location with the Command Center for optimized dispatching.
- **SOS Alerts:** One-touch emergency signaling for immediate assistance.
- **Real-Time Notifications:** Receive broadcast alerts and direct commands via WebSockets.
- **Authentication:** Secure login and role management powered by **Supabase**.

## 🛠 Technology Stack

- **Framework:** React Native / Expo
- **Language:** TypeScript
- **Auth & Database:** Supabase
- **Real-Time:** Socket.io-client
- **Navigation:** Expo Router (Stack/Tabs)
- **Location:** Expo Location & React Native Maps
- **State Management:** React Hooks

## 🚀 Setup Instructions

1. **Install Dependencies:**
   ```bash
   npm install
   ```
2. **Environment Variables:**
   - Update `.env` with your `EXPO_PUBLIC_SOCKET_URL` (use your machine's IP for physical devices).
   - Configure your Supabase URL and Anon Key.
3. **Launch:**
   ```bash
   npx expo start
   ```
   - Open via **Expo Go** on Android/iOS or use an emulator.
