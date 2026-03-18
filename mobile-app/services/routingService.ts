import axios from 'axios';

// Update with your actual server IP or use process.env.EXPO_PUBLIC_API_URL
const API_BASE = "http://localhost:8000"; 

export interface RouteStep {
  distance: { text: string; value: number };
  duration: { text: string; value: number };
  duration_in_traffic?: { text: string; value: number };
  end_location: { lat: number; lng: number };
  start_location: { lat: number; lng: number };
  html_instructions: string;
  polyline: { points: string };
  travel_mode: string;
}

export interface RouteLeg {
  distance: { text: string; value: number };
  duration: { text: string; value: number };
  duration_in_traffic?: { text: string; value: number };
  end_address: string;
  end_location: { lat: number; lng: number };
  start_address: string;
  start_location: { lat: number; lng: number };
  steps: RouteStep[];
}

export interface DirectionsResponse {
  routes: {
    legs: RouteLeg[];
    overview_polyline: { points: string };
    summary: string;
  }[];
  status: string;
}

export const RoutingService = {
  /**
   * Fetches traffic-aware directions from the backend.
   */
  getDirections: async (origin: string, destination: string): Promise<DirectionsResponse> => {
    try {
      const response = await axios.get(`${API_BASE}/api/directions`, {
        params: {
          origin,
          destination,
          departure_time: 'now'
        }
      });
      return response.data;
    } catch (error) {
      console.error("Failed to fetch routing data", error);
      throw error;
    }
  }
};
