import React, { useState, useEffect } from 'react';
import { StyleSheet, TouchableOpacity, Alert, View, ScrollView } from 'react-native';
import { useRouter } from 'expo-router';

import { HelloWave } from '@/components/hello-wave';
import ParallaxScrollView from '@/components/parallax-scroll-view';
import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { IconSymbol } from '@/components/ui/icon-symbol';
import { useLocation } from '@/hooks/useLocation';
import SocketService from '@/services/socketService';
import { LocationService } from '@/services/locationService';
import { AuthService, UserProfile } from '@/services/authService';
import BLEMeshService, { MeshNode, SOSMessage } from '@/services/bleService';

export default function DashboardScreen() {
  const router = useRouter();
  const { location, errorMsg, loading, refreshLocation } = useLocation();
  const [isSharing, setIsSharing] = useState(false);
  const [subscription, setSubscription] = useState<any>(null);
  const [user, setUser] = useState<UserProfile | null>(null);

  // Offline Resilience (BLE Mesh)
  const [isMeshActive, setIsMeshActive] = useState(false);
  const [meshNodes, setMeshNodes] = useState<MeshNode[]>([]);
  const [incomingSOS, setIncomingSOS] = useState<SOSMessage[]>([]);

  useEffect(() => {
    SocketService.connect();
    loadUser();
    
    // Initialize BLE Mesh
    BLEMeshService.initialize().then(() => {
      BLEMeshService.onSOSReceived((message) => {
        setIncomingSOS((prev) => [message, ...prev].slice(0, 5)); // Keep last 5
        Alert.alert(
          'OFFLINE SOS RECEIVED', 
          `Critical alert relayed from mesh node!\nHops: ${message.hops}\nStatus: ${message.status.toUpperCase()}`
        );
      });
    });

    return () => {
      stopLocationUpdates();
      SocketService.disconnect();
      if (isMeshActive) BLEMeshService.stopScanning();
    };
  }, []);

  const loadUser = async () => {
    const profile = await AuthService.getCurrentUser();
    setUser(profile);
  };

  const handleLogout = async () => {
    await AuthService.signOut();
    router.replace('/auth' as any);
  };

  const startLocationUpdates = async () => {
    const sub = await LocationService.watchLocation((newLocation) => {
      SocketService.emit('send_location', {
        name: user?.fullName || 'Anonymous User',
        role: user?.role || 'citizen',
        coords: newLocation.coords,
        timestamp: newLocation.timestamp,
      });
    });

    if (sub) {
      setSubscription(sub);
      setIsSharing(true);
    } else {
      Alert.alert('Permission Denied', 'Please enable location permissions in settings.');
    }
  };

  const stopLocationUpdates = () => {
    if (subscription) {
      subscription.remove();
      setSubscription(null);
    }
    setIsSharing(false);
  };

  const toggleSharing = () => {
    if (isSharing) {
      stopLocationUpdates();
    } else {
      startLocationUpdates();
    }
  };

  const toggleMeshNetwork = () => {
    if (isMeshActive) {
      BLEMeshService.stopScanning();
      setIsMeshActive(false);
      setMeshNodes([]);
    } else {
      BLEMeshService.startScanning((nodes) => {
        setMeshNodes(nodes);
      });
      setIsMeshActive(true);
    }
  };

  const triggerSOS = () => {
    Alert.alert(
      'SOS Alert',
      'Choose how to broadcast your emergency alert.',
      [
        { text: 'Cancel', style: 'cancel' },
        { 
          text: 'Send via Network', 
          onPress: () => {
            SocketService.emit('sos_alert', {
              name: user?.fullName || 'Anonymous User',
              location: location?.coords,
              timestamp: Date.now(),
            });
            Alert.alert('SOS Sent', 'Your SOS alert has been broadcasted via Internet.');
          }
        },
        { 
          text: 'Send via Offline Mesh (BLE)', 
          style: 'destructive',
          onPress: async () => {
            if (!location) {
              Alert.alert('Error', 'Location required for offline SOS.');
              return;
            }
            const success = await BLEMeshService.broadcastSOS(
              location.coords.latitude,
              location.coords.longitude,
              'critical'
            );
            if (success) Alert.alert('Offline SOS Sent', 'Your alert was broadcasted to nearby peer devices via Bluetooth.');
          }
        },
      ]
    );
  };

  return (
    <ParallaxScrollView
      headerBackgroundColor={{ light: '#ff3b3b', dark: '#9b1a1a' }}
      headerImage={
        <ThemedView style={styles.headerIconContainer}>
           <IconSymbol
            size={120}
            color="white"
            name="antenna.radiowaves.left.and.right"
            style={styles.headerIcon}
          />
        </ThemedView>
      }>
      <ThemedView style={styles.titleContainer}>
        <View>
          <ThemedText type="title">{user?.role === 'responder' ? 'Responder' : 'Citizen'} Dashboard</ThemedText>
          <ThemedText style={{ opacity: 0.6 }}>Welcome, {user?.fullName || 'User'}</ThemedText>
        </View>
        <HelloWave />
      </ThemedView>

      <ThemedView style={styles.statusCard}>
        <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
          <ThemedText type="subtitle">GPS Tracking</ThemedText>
          <TouchableOpacity onPress={handleLogout}>
             <ThemedText style={{ color: '#ff3b3b', fontSize: 12, fontWeight: 'bold' }}>LOGOUT</ThemedText>
          </TouchableOpacity>
        </View>
        <ThemedView style={styles.statusRow}>
          <View style={[styles.statusDot, { backgroundColor: isSharing ? '#00ff9d' : '#ff3b3b' }]} />
          <ThemedText>{isSharing ? 'Live Tracking Active' : 'Tracking Offline'}</ThemedText>
        </ThemedView>
        
        {location && (
          <ThemedView style={styles.locationInfo}>
            <ThemedText type="defaultSemiBold">Current Coordinates:</ThemedText>
            <ThemedText>{location.coords.latitude.toFixed(6)}, {location.coords.longitude.toFixed(6)}</ThemedText>
          </ThemedView>
        )}

        <View style={styles.buttonRow}>
          <TouchableOpacity 
            style={[styles.button, { flex: 1, backgroundColor: isSharing ? '#ff3b3b' : '#00d4ff' }]} 
            onPress={toggleSharing}
          >
            <ThemedText style={styles.buttonText}>
              {isSharing ? 'Stop Tracking' : 'Start Tracking'}
            </ThemedText>
          </TouchableOpacity>

          <TouchableOpacity 
            style={styles.refreshButton} 
            onPress={refreshLocation}
            disabled={loading}
          >
            <IconSymbol name="arrow.clockwise" size={24} color="white" />
          </TouchableOpacity>
        </View>
      </ThemedView>

      {/* Offline Resilience Card */}
      <ThemedView style={styles.meshCard}>
        <View style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
          <ThemedText type="subtitle">BLE Mesh Network (Offline)</ThemedText>
          <View style={[styles.statusDot, { backgroundColor: isMeshActive ? '#00d4ff' : '#8aa3b8' }]} />
        </View>
        <ThemedText style={styles.meshDesc}>Connect directly to nearby devices via Bluetooth when cellular networks fail.</ThemedText>
        
        <TouchableOpacity 
          style={[styles.meshButton, { backgroundColor: isMeshActive ? '#1a1f26' : '#00d4ff' }]} 
          onPress={toggleMeshNetwork}
        >
          <ThemedText style={styles.meshButtonText}>
            {isMeshActive ? 'Disable Mesh Network' : 'Enable Offline Mesh'}
          </ThemedText>
        </TouchableOpacity>

        {isMeshActive && (
          <View style={styles.meshStats}>
            <ThemedText style={{ fontSize: 12, color: '#00d4ff' }}>Nodes Found: {meshNodes.length}</ThemedText>
          </View>
        )}
      </ThemedView>

      <TouchableOpacity style={styles.sosButton} onPress={triggerSOS}>
        <ThemedText style={styles.sosText}>TRIGGER SOS</ThemedText>
      </TouchableOpacity>

      <ThemedView style={styles.stepContainer}>
        <ThemedText type="subtitle">Operational Info</ThemedText>
        <ThemedText>
          When active, your location is shared with the Command Center in real-time. Ensure your device has a clear GPS signal.
        </ThemedText>
      </ThemedView>

      {errorMsg && (
        <ThemedView style={styles.errorContainer}>
          <ThemedText style={styles.errorText}>{errorMsg}</ThemedText>
        </ThemedView>
      )}
    </ParallaxScrollView>
  );
}

const styles = StyleSheet.create({
  headerIconContainer: {
    height: 250,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: 'transparent',
  },
  headerIcon: {
    bottom: 0,
    position: 'absolute',
  },
  titleContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginBottom: 16,
  },
  statusCard: {
    padding: 16,
    borderRadius: 12,
    backgroundColor: 'rgba(255,255,255,0.05)',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
    marginBottom: 16,
  },
  meshCard: {
    padding: 16,
    borderRadius: 12,
    backgroundColor: 'rgba(0, 212, 255, 0.05)',
    borderWidth: 1,
    borderColor: 'rgba(0, 212, 255, 0.2)',
    marginBottom: 16,
  },
  meshDesc: {
    fontSize: 12,
    color: '#8aa3b8',
    marginTop: 8,
    marginBottom: 12,
  },
  meshButton: {
    padding: 12,
    borderRadius: 8,
    alignItems: 'center',
  },
  meshButtonText: {
    color: 'white',
    fontWeight: '700',
    fontSize: 14,
  },
  meshStats: {
    marginTop: 10,
    paddingTop: 10,
    borderTopWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
  },
  statusRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    marginTop: 8,
    marginBottom: 16,
  },
  statusDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
  },
  locationInfo: {
    marginBottom: 16,
    padding: 8,
    backgroundColor: 'rgba(0,0,0,0.2)',
    borderRadius: 8,
  },
  buttonRow: {
    flexDirection: 'row',
    gap: 8,
  },
  button: {
    padding: 14,
    borderRadius: 8,
    alignItems: 'center',
  },
  refreshButton: {
    width: 50,
    padding: 14,
    borderRadius: 8,
    backgroundColor: 'rgba(255,255,255,0.1)',
    alignItems: 'center',
    justifyContent: 'center',
  },
  buttonText: {
    color: 'white',
    fontWeight: '700',
    fontSize: 16,
  },
  sosButton: {
    backgroundColor: '#ff3b3b',
    padding: 20,
    borderRadius: 12,
    alignItems: 'center',
    marginBottom: 16,
    borderWidth: 2,
    borderColor: 'white',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 4,
    elevation: 8,
  },
  sosText: {
    color: 'white',
    fontWeight: '900',
    fontSize: 22,
    letterSpacing: 2,
  },
  stepContainer: {
    gap: 8,
    marginBottom: 16,
  },
  errorContainer: {
    padding: 12,
    backgroundColor: 'rgba(255,59,59,0.1)',
    borderRadius: 8,
    marginTop: 8,
  },
  errorText: {
    color: '#ff3b3b',
    fontSize: 12,
  },
});
