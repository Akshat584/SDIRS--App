import axios from 'axios';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { API_BASE } from './apiConfig';

export type UserRole = 'citizen' | 'responder' | 'admin' | 'ops';

export interface UserProfile {
  id: string | number;
  email: string;
  role: UserRole;
  fullName: string;
}

const TOKEN_KEY = 'sdirs_auth_token';

export const AuthService = {
  /**
   * Signs up a new user via the backend API.
   */
  signUp: async (email: string, password: string, fullName: string, role: UserRole) => {
    try {
      const response = await axios.post(`${API_BASE}/api/auth/register`, {
        name: fullName,
        email,
        password,
        role
      });
      return { user: response.data, error: null };
    } catch (error: any) {
      console.error('Sign up error:', error.response?.data?.detail || error.message);
      return { user: null, error: error.response?.data?.detail || error.message };
    }
  },

  /**
   * Signs in an existing user via the backend API.
   */
  signIn: async (email: string, password: string) => {
    try {
      const formData = new FormData();
      formData.append('username', email);
      formData.append('password', password);

      const response = await axios.post(`${API_BASE}/api/auth/login`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      
      const { access_token } = response.data;
      await AsyncStorage.setItem(TOKEN_KEY, access_token);
      
      return { session: response.data, error: null };
    } catch (error: any) {
      console.error('Sign in error:', error.response?.data?.detail || error.message);
      return { session: null, error: error.response?.data?.detail || error.message };
    }
  },

  /**
   * Signs out the current user.
   */
  signOut: async () => {
    try {
      await AsyncStorage.removeItem(TOKEN_KEY);
    } catch (error) {
      console.error('Sign out error:', error);
    }
  },

  /**
   * Fetches the current user's profile from the backend.
   */
  getCurrentUser: async (): Promise<UserProfile | null> => {
    try {
      const token = await AsyncStorage.getItem(TOKEN_KEY);
      if (!token) return null;

      const response = await axios.get(`${API_BASE}/api/auth/me`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      const user = response.data;
      return {
        id: user.id,
        email: user.email,
        role: user.role as UserRole,
        fullName: user.name,
      };
    } catch (error) {
      console.error('[AuthService] Error fetching current user:', error);
      // If token is invalid/expired, clear it
      await AsyncStorage.removeItem(TOKEN_KEY);
      return null;
    }
  }
};
