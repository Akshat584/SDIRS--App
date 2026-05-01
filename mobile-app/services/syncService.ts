import AsyncStorage from '@react-native-async-storage/async-storage';
import axios from 'axios';
import { API_BASE } from './apiConfig';

const OFFLINE_QUEUE_KEY = '@sdirs_offline_queue';

interface OfflineIncident {
  id: string;
  data: any;
  timestamp: number;
}

class SyncService {
  /**
   * Adds an incident report to the offline queue.
   */
  static async queueIncident(incidentData: any) {
    try {
      const queueJson = await AsyncStorage.getItem(OFFLINE_QUEUE_KEY);
      const queue: OfflineIncident[] = queueJson ? JSON.parse(queueJson) : [];
      
      const newIncident: OfflineIncident = {
        id: Math.random().toString(36).substring(7),
        data: incidentData,
        timestamp: Date.now(),
      };
      
      queue.push(newIncident);
      await AsyncStorage.setItem(OFFLINE_QUEUE_KEY, JSON.stringify(queue));
      console.log('Incident queued for offline sync.');
    } catch (error) {
      console.error('Failed to queue incident:', error);
    }
  }

  /**
   * Attempts to sync all queued incidents with the backend.
   */
  static async syncQueue() {
    try {
      const queueJson = await AsyncStorage.getItem(OFFLINE_QUEUE_KEY);
      if (!queueJson) return;

      const queue: OfflineIncident[] = JSON.parse(queueJson);
      if (queue.length === 0) return;

      console.log(`Attempting to sync ${queue.length} incidents...`);

      const successfulIds: string[] = [];

      for (const item of queue) {
        try {
          const formData = new FormData();
          Object.keys(item.data).forEach(key => {
            formData.append(key, item.data[key]);
          });

          await axios.post(`${API_BASE}/incidents`, formData, {
            headers: {
              'Content-Type': 'multipart/form-data',
            },
          });
          
          successfulIds.push(item.id);
        } catch (error) {
          console.error(`Failed to sync incident ${item.id}:`, error);
          // Stop syncing if we hit a network error
          break;
        }
      }

      // Remove successful items from queue
      const remainingQueue = queue.filter(item => !successfulIds.includes(item.id));
      await AsyncStorage.setItem(OFFLINE_QUEUE_KEY, JSON.stringify(remainingQueue));
      
      if (successfulIds.length > 0) {
        console.log(`Successfully synced ${successfulIds.length} incidents.`);
      }
    } catch (error) {
      console.error('Sync failed:', error);
    }
  }

  /**
   * Gets the number of pending incidents in the queue.
   */
  static async getQueueCount(): Promise<number> {
    const queueJson = await AsyncStorage.getItem(OFFLINE_QUEUE_KEY);
    if (!queueJson) return 0;
    const queue = JSON.parse(queueJson);
    return queue.length;
  }
}

export default SyncService;
