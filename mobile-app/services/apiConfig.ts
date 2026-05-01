/**
 * SDIRS API Configuration
 * Centralizes all backend endpoints and external service URLs.
 *
 * IMPORTANT: For physical device testing, create mobile-app/.env file with:
 * EXPO_PUBLIC_API_URL=http://YOUR_LOCAL_IP:8000
 * EXPO_PUBLIC_SOCKET_URL=http://YOUR_LOCAL_IP:8000
 *
 * To find your local IP: ipconfig (Windows) or ifconfig (Mac/Linux)
 */

export const API_CONFIG = {
  // Backend API base URL - set via environment variable
  // For physical device testing, use your computer's local IP (e.g., http://192.168.1.100:8000)
  API_BASE: process.env.EXPO_PUBLIC_API_URL || 'http://localhost:8000',

  // Socket.IO server URL - set via environment variable
  SOCKET_URL: process.env.EXPO_PUBLIC_SOCKET_URL || 'http://localhost:8000',

  // Supabase configuration
  SUPABASE_URL: process.env.EXPO_PUBLIC_SUPABASE_URL || 'https://your-project-url.supabase.co',
  SUPABASE_ANON_KEY: process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY || 'your-anon-key',

  // API Endpoints
  ENDPOINTS: {
    INCIDENTS: '/api/incidents',
    HEATMAP: '/api/heatmap',
    ROUTING: '/api/directions',
    PREDICTIONS: '/api/predictions',
    MESSAGES: '/api/messages',
  },

  // App configuration
  APP: {
    NAME: 'SDIRS - Disaster Response',
    VERSION: '1.0.0',
    ENVIRONMENT: process.env.EXPO_PUBLIC_ENV || 'development',
  },
};

export const API_BASE = API_CONFIG.API_BASE;
export const ENDPOINTS = API_CONFIG.ENDPOINTS;

export default API_CONFIG;
