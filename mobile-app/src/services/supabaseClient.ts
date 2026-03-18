import 'react-native-url-polyfill/auto';
import AsyncStorage from '@react-native-async-storage/async-storage';
import { createClient } from '@supabase/supabase-js';

// These should be added to your .env file
const supabaseUrl = process.env.EXPO_PUBLIC_SUPABASE_URL || 'https://pyojhnglvqpkmogyyizk.supabase.co';
const supabaseAnonKey = process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY || 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InB5b2pobmdsdnFwa21vZ3l5aXprIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzMyODE0NTMsImV4cCI6MjA4ODg1NzQ1M30.6UkNNWq_t1M25Y5NreleCs9sFMomocR9NTR8Y5fegq0';

export const supabase = createClient(supabaseUrl, supabaseAnonKey, {
  auth: {
    storage: AsyncStorage,
    autoRefreshToken: true,
    persistSession: true,
    detectSessionInUrl: false,
  },
});
