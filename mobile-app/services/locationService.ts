import * as Location from 'expo-location';

/**
 * Service to handle location-related operations.
 */
export const LocationService = {
  /**
   * Requests foreground location permissions.
   * @returns {Promise<boolean>} True if granted, false otherwise.
   */
  requestPermissions: async (): Promise<boolean> => {
    const { status } = await Location.requestForegroundPermissionsAsync();
    return status === 'granted';
  },

  /**
   * Gets the current location of the device.
   * @returns {Promise<Location.LocationObject | null>} The current location object or null if failed.
   */
  getCurrentLocation: async (): Promise<Location.LocationObject | null> => {
    try {
      const hasPermission = await LocationService.requestPermissions();
      if (!hasPermission) {
        console.warn('Location permission not granted');
        return null;
      }

      const location = await Location.getCurrentPositionAsync({
        accuracy: Location.Accuracy.Balanced,
      });
      return location;
    } catch (error) {
      console.error('Error fetching location:', error);
      return null;
    }
  },

  /**
   * Watches the device's location in real-time.
   * @param {Function} callback Callback function to handle location updates.
   * @returns {Promise<Location.LocationSubscription>} A subscription object to stop watching.
   */
  watchLocation: async (callback: (location: Location.LocationObject) => void) => {
    const hasPermission = await LocationService.requestPermissions();
    if (!hasPermission) return null;

    return await Location.watchPositionAsync(
      {
        accuracy: Location.Accuracy.High,
        distanceInterval: 10, // Update every 10 meters
      },
      callback
    );
  },
};
