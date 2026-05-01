import { useState, useEffect, useCallback } from 'react';
import * as Location from 'expo-location';
import { LocationService } from '@/services/locationService';

export const useLocation = () => {
  const [location, setLocation] = useState<Location.LocationObject | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshLocation = useCallback(async () => {
    setLoading(true);
    setErrorMsg(null);

    try {
      const current = await LocationService.getCurrentLocation();

      if (current) {
        setLocation(current);
      } else {
        setErrorMsg('Permission to access location was denied');
      }
    } catch (error: any) {
      const errorMessage = error?.message || 'Unknown error';
      setErrorMsg(`Error fetching location: ${errorMessage}`);
      console.error('[useLocation] Error:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    let subscription: any = null;

    const initLocation = async () => {
      try {
        await refreshLocation();

        subscription = await LocationService.watchLocation((newLocation) => {
          setLocation(newLocation);
        });
      } catch (error) {
        console.error('[useLocation] Error starting location watch:', error);
      }
    };

    initLocation();

    return () => {
      if (subscription?.remove) {
        subscription.remove();
      }
    };
  }, [refreshLocation]);

  return { location, errorMsg, loading, refreshLocation };
};
