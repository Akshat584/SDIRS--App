import React, { useState, useEffect, useCallback, memo } from 'react';
import { StyleSheet, FlatList, View } from 'react-native';

import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { IconSymbol } from '@/components/ui/icon-symbol';
import SocketService from '@/services/socketService';
import { AlertService, AlertItem } from '@/services/alertService';
import { useLocation } from '@/hooks/useLocation';

const AlertCard = memo(function AlertCard({ item }: { item: AlertItem }) {
  return (
    <ThemedView style={[styles.alertCard, styles[item.severity]]}>
      <View style={styles.alertHeader}>
        <IconSymbol 
          name={item.severity === 'high' ? 'exclamationmark.octagon.fill' : 'info.circle.fill'} 
          size={24} 
          color="white" 
        />
        <ThemedText style={styles.alertType}>{item.type}</ThemedText>
      </View>
      <ThemedText style={styles.alertMessage}>{item.message}</ThemedText>
      <ThemedText style={styles.alertTime}>
        {new Date(item.timestamp).toLocaleTimeString()}
      </ThemedText>
    </ThemedView>
  );
});

export default function AlertsScreen() {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);
  const { location } = useLocation();

  const loadAlerts = useCallback(async () => {
    try {
      // 1. Fetch historical/active incidents as alerts
      const incidentAlerts = await AlertService.getIncidentAlerts();
      
      // 2. Fetch weather alerts based on location
      let weatherAlerts: AlertItem[] = [];
      if (location?.coords) {
        weatherAlerts = await AlertService.getWeatherAlerts(
          location.coords.latitude,
          location.coords.longitude
        );
      }

      // 3. Combine and sort by timestamp
      const combined = [...weatherAlerts, ...incidentAlerts].sort((a, b) => b.timestamp - a.timestamp);
      setAlerts(combined);
    } catch (err) {
      console.error("Failed to load alerts:", err);
    }
  }, [location]);

  useEffect(() => {
    loadAlerts();

    // Listen for real-time alerts
    const handleNewAlert = (newAlert: AlertItem) => {
      setAlerts((prev) => {
        // Avoid duplicates if same ID
        if (prev.find(a => a.id === newAlert.id)) return prev;
        return [newAlert, ...prev];
      });
    };

    SocketService.on('emergency_alert', handleNewAlert);

    return () => {
      SocketService.off('emergency_alert', handleNewAlert);
    };
  }, [loadAlerts]);

  const renderItem = useCallback(({ item }: { item: AlertItem }) => <AlertCard item={item} />, []);
  const keyExtractor = useCallback((item: AlertItem) => item.id, []);

  return (
    <ThemedView style={styles.container}>
      <FlatList
        data={alerts}
        keyExtractor={keyExtractor}
        renderItem={renderItem}
        contentContainerStyle={styles.listContent}
        initialNumToRender={10}
        maxToRenderPerBatch={10}
        windowSize={5}
        removeClippedSubviews={true}
        ListEmptyComponent={
          <View style={styles.emptyState}>
            <IconSymbol name="bell.slash.fill" size={48} color="rgba(255,255,255,0.2)" />
            <ThemedText style={styles.emptyText}>No active alerts at this time.</ThemedText>
          </View>
        }
      />
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  listContent: {
    padding: 16,
    paddingTop: 8,
  },
  alertCard: {
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
  },
  high: {
    backgroundColor: '#9b1a1a',
  },
  medium: {
    backgroundColor: '#b8860b',
  },
  low: {
    backgroundColor: '#2e8b57',
  },
  alertHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 8,
  },
  alertType: {
    fontSize: 18,
    fontWeight: 'bold',
    color: 'white',
  },
  alertMessage: {
    fontSize: 15,
    color: 'rgba(255,255,255,0.9)',
    marginBottom: 8,
  },
  alertTime: {
    fontSize: 12,
    color: 'rgba(255,255,255,0.6)',
    textAlign: 'right',
  },
  emptyState: {
    alignItems: 'center',
    marginTop: 100,
  },
  emptyText: {
    marginTop: 16,
    opacity: 0.5,
  },
});
