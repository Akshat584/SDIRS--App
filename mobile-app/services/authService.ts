import { supabase } from './supabaseClient';
import { Alert } from 'react-native';

export type UserRole = 'citizen' | 'responder';

export interface UserProfile {
  id: string;
  email: string;
  role: UserRole;
  fullName: string;
}

export const AuthService = {
  /**
   * Signs up a new user and assigns them a role.
   * In a real Supabase setup, roles are often stored in a 'profiles' table.
   */
  signUp: async (email: string, password: string, fullName: string, role: UserRole) => {
    try {
      const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
          data: {
            full_name: fullName,
            role: role,
          },
        },
      });

      if (error) throw error;
      
      // Note: In production, you would have a database trigger to insert 
      // this into a 'profiles' table after auth.signUp.
      return { user: data.user, error: null };
    } catch (error: any) {
      console.error('Sign up error:', error.message);
      return { user: null, error: error.message };
    }
  },

  /**
   * Signs in an existing user.
   */
  signIn: async (email: string, password: string) => {
    try {
      const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password,
      });

      if (error) throw error;
      return { session: data.session, error: null };
    } catch (error: any) {
      console.error('Sign in error:', error.message);
      return { session: null, error: error.message };
    }
  },

  /**
   * Signs out the current user.
   */
  signOut: async () => {
    const { error } = await supabase.auth.signOut();
    if (error) {
      console.error('Sign out error:', error.message);
    }
  },

  /**
   * Fetches the current user's profile and role.
   */
  getCurrentUser: async (): Promise<UserProfile | null> => {
    const { data: { user } } = await supabase.auth.getUser();
    
    if (!user) return null;

    return {
      id: user.id,
      email: user.email || '',
      role: (user.user_metadata?.role as UserRole) || 'citizen',
      fullName: user.user_metadata?.full_name || 'User',
    };
  }
};
