import { useState, useEffect, useCallback } from 'react';
import * as Location from 'expo-location';
import { LocationService } from '@/services/locationService';

export const useLocation = () => {
  const [location, setLocation] = useState<Location.LocationObject | null>(null);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  const refreshLocation = useCallback(async () => {
    setLoading(true);
    try {
      const current = await LocationService.getCurrentLocation();
      if (current) {
        setLocation(current);
      } else {
        setErrorMsg('Permission to access location was denied');
      }
    } catch (error) {
      setErrorMsg('Error fetching location');
      console.error(error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    let subscription: any = null;

    const initLocation = async () => {
      await refreshLocation();
      
      try {
        subscription = await LocationService.watchLocation((newLocation) => {
          setLocation(newLocation);
        });
      } catch (error) {
        console.error('Error starting location watch:', error);
      }
    };

    initLocation();

    return () => {
      if (subscription) {
        subscription.remove();
      }
    };
  }, [refreshLocation]);

  return { location, errorMsg, loading, refreshLocation };
};
