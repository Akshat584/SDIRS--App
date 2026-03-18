import axios from 'axios';

const API_BASE = "http://localhost:8000"; // Update with your actual server IP

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
  getHeatmapData: async (lat: number, lon: number): Promise<HeatmapResponse> => {
    try {
      const response = await axios.get(`${API_BASE}/api/heatmap`, {
        params: { lat, lon, radius: 5000 }
      });
      return response.data;
    } catch (error) {
      console.error("Failed to fetch heatmap data", error);
      throw error;
    }
  }
};
