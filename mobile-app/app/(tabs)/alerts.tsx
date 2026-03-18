import React, { useState, useEffect } from 'react';
import { StyleSheet, FlatList, View } from 'react-native';

import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { IconSymbol } from '@/components/ui/icon-symbol';
import SocketService from '@/services/socketService';

interface AlertItem {
  id: string;
  type: string;
  message: string;
  severity: 'high' | 'medium' | 'low';
  timestamp: number;
}

export default function AlertsScreen() {
  const [alerts, setAlerts] = useState<AlertItem[]>([]);

  useEffect(() => {
    // Listen for real-time alerts
    SocketService.on('emergency_alert', (newAlert: AlertItem) => {
      setAlerts((prev) => [newAlert, ...prev]);
    });

    // Mock initial alerts for demonstration
    setAlerts([
      {
        id: '1',
        type: 'Flood Warning',
        message: 'Heavy rainfall expected in the downtown area. Seek higher ground.',
        severity: 'high',
        timestamp: Date.now() - 1000 * 60 * 30,
      },
      {
        id: '2',
        type: 'Road Closure',
        message: 'Main St closed due to fallen trees.',
        severity: 'medium',
        timestamp: Date.now() - 1000 * 60 * 60 * 2,
      },
    ]);
  }, []);

  const renderItem = ({ item }: { item: AlertItem }) => (
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

  return (
    <ThemedView style={styles.container}>
      <FlatList
        data={alerts}
        keyExtractor={(item) => item.id}
        renderItem={renderItem}
        contentContainerStyle={styles.listContent}
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
