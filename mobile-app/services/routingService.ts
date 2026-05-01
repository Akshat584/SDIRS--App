import axios from 'axios';
import { API_BASE, ENDPOINTS } from './apiConfig';

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
  getDirections: async (
    origin: string,
    destination: string,
    departureTime: string = 'now'
  ): Promise<DirectionsResponse> => {
    try {
      const response = await axios.get(`${API_BASE}${ENDPOINTS.ROUTING}`, {
        params: {
          origin,
          destination,
          departure_time: departureTime,
        },
        timeout: 15000, // 15 second timeout
      });
      return response.data;
    } catch (error: any) {
      console.error('[RoutingService] Failed to fetch directions:', error.message);
      throw new Error(error.response?.data?.message || 'Failed to fetch route');
    }
  }
};
