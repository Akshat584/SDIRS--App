import axios from 'axios';
import { API_BASE } from './apiConfig';

export interface AlertItem {
  id: string;
  type: string;
  message: string;
  severity: 'high' | 'medium' | 'low';
  timestamp: number;
}

export const AlertService = {
  /**
   * Fetches the latest weather alerts from the backend.
   */
  getWeatherAlerts: async (lat: number, lon: number): Promise<AlertItem[]> => {
    try {
      const response = await axios.get(`${API_BASE}/api/weather-alerts`, {
        params: { lat, lon },
        timeout: 10000,
      });

      if (!response.data || !response.data.alerts) return [];

      return response.data.alerts.map((alert: any, index: number) => ({
        id: `weather-${index}-${Date.now()}`,
        type: alert.event || 'Weather Alert',
        message: alert.description || 'No description available.',
        severity: alert.severity === 'Extreme' ? 'high' : alert.severity === 'Severe' ? 'medium' : 'low',
        timestamp: alert.start * 1000 || Date.now(),
      }));
    } catch (error: any) {
      console.error('[AlertService] Failed to fetch weather alerts:', error.message);
      return [];
    }
  },

  /**
   * Fetches recent incidents that might serve as alerts.
   */
  getIncidentAlerts: async (): Promise<AlertItem[]> => {
    try {
      const response = await axios.get(`${API_BASE}/api/incidents`, {
        timeout: 10000,
      });

      if (!response.data) return [];

      return response.data.map((inc: any) => ({
        id: `inc-${inc.id}`,
        type: inc.incident_type || 'Incident',
        message: inc.description || 'New incident reported.',
        severity: inc.predicted_severity === 'critical' || inc.predicted_severity === 'high' ? 'high' : 'medium',
        timestamp: Date.now(), // Real incidents should have timestamps
      }));
    } catch (error: any) {
      console.error('[AlertService] Failed to fetch incident alerts:', error.message);
      return [];
    }
  }
};
