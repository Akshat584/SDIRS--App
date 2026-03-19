/**
 * SDIRS API Configuration
 * Centralizes all backend endpoints.
 */

// In development, replace 'localhost' with your machine's local IP (e.g., 192.168.1.15)
// to allow physical devices and emulators to connect.
const DEFAULT_API_URL = 'http://192.168.68.182:8000';

export const API_BASE = process.env.EXPO_PUBLIC_API_URL || DEFAULT_API_URL;

export const ENDPOINTS = {
  INCIDENTS: `${API_BASE}/api/incidents`,
  HEATMAP: `${API_BASE}/api/heatmap`,
  ROUTING: `${API_BASE}/api/routing`,
  PREDICTIONS: `${API_BASE}/api/predictions`,
  MESSAGES: `${API_BASE}/api/messages`,
};

export default {
  API_BASE,
  ENDPOINTS,
};
