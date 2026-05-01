import axios from 'axios';
import { API_BASE, ENDPOINTS } from './apiConfig';

export interface HeatmapPoint {
  lat: number;
  lon: number;
  intensity: number;
  type: 'incident' | 'prediction' | 'hazard';
  label: string;
  radius: number;
}

export interface HeatmapResponse {
  points: HeatmapPoint[];
  timestamp: string;
}

export const HeatmapService = {
  /**
   * Fetches heatmap data from the backend.
   */
  getHeatmapData: async (lat: number, lon: number, radius: number = 5000): Promise<HeatmapResponse> => {
    try {
      const response = await axios.get(`${API_BASE}${ENDPOINTS.HEATMAP}`, {
        params: { lat, lon, radius },
        timeout: 10000, // 10 second timeout
      });
      return response.data;
    } catch (error: any) {
      console.error('[HeatmapService] Failed to fetch heatmap data:', error.message);
      throw new Error(error.response?.data?.message || 'Failed to fetch heatmap data');
    }
  }
};
