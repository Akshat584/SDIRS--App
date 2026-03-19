import React, { useEffect, useState, useCallback } from 'react';
import { StyleSheet, View, Text } from 'react-native';
import MapView, { Circle, Marker, Polyline } from 'react-native-maps';

import { ThemedText } from '@/components/themed-text';
import { useLocation } from '@/hooks/useLocation';
import SocketService from '@/services/socketService';
import { AuthService, UserProfile } from '@/services/authService';
import { HeatmapService, HeatmapPoint } from '@/services/heatmapService';
import { RoutingService } from '@/services/routingService';

export default function MapScreen() {
  const { location, loading } = useLocation();
  const [user, setUser] = useState<UserProfile | null>(null);
  const [heatmapPoints, setHeatmapPoints] = useState<HeatmapPoint[]>([]);
  const [routeCoordinates, setRouteCoordinates] = useState<{ latitude: number, longitude: number }[]>([]);
  const [assignedIncident, setAssignedIncident] = useState<{ id: string, latitude: number, longitude: number, title: string } | null>(null);

  const [trackedUsers, setTrackedUsers] = useState<Record<string, {
    id: string;
    name: string;
    role: string;
    latitude: number;
    longitude: number;
    timestamp: number;
  }>>({});

  // Helper to decode Google Maps Polyline
  const decodePolyline = (t: string) => {
    let points = [];
    for (let step, shift = 0, result = 0, byte = null, lat = 0, lng = 0, i = 0; i < t.length; ) {
      for (shift = 0, result = 0; byte = t.charCodeAt(i++) - 63, result |= (31 & byte) << shift, shift += 5, 31 <= byte; );
      lat += 1 & result ? ~(result >> 1) : result >> 1;
      for (shift = 0, result = 0; byte = t.charCodeAt(i++) - 63, result |= (31 & byte) << shift, shift += 5, 31 <= byte; );
      lng += 1 & result ? ~(result >> 1) : result >> 1;
      points.push({ latitude: lat / 1e5, longitude: lng / 1e5 });
    }
    return points;
  };
  const [initialRegion, setInitialRegion] = useState({
    latitude: 37.78825,
    longitude: -122.4324,
    latitudeDelta: 0.0922,
    longitudeDelta: 0.0421,
  });

  useEffect(() => {
    if (location) {
      setInitialRegion({
        latitude: location.coords.latitude,
        longitude: location.coords.longitude,
        latitudeDelta: 0.05,
        longitudeDelta: 0.05,
      });
      fetchHeatmap(location.coords.latitude, location.coords.longitude);
      if (assignedIncident) {
        fetchRoute(
          `${location.coords.latitude},${location.coords.longitude}`,
          `${assignedIncident.latitude},${assignedIncident.longitude}`
        );
      }
    }
  }, [location, assignedIncident]);

  const fetchRoute = async (origin: string, destination: string) => {
    try {
      const directions = await RoutingService.getDirections(origin, destination);
      if (directions.routes.length > 0) {
        const points = decodePolyline(directions.routes[0].overview_polyline.points);
        setRouteCoordinates(points);
      }
    } catch (err) {
      console.error("Routing error:", err);
    }
  };

  const fetchHeatmap = async (lat: number, lon: number) => {
    try {
      const data = await HeatmapService.getHeatmapData(lat, lon);
      setHeatmapPoints(data.points);
    } catch (err) {
      console.error("Heatmap fetch error:", err);
    }
  };

  useEffect(() => {
    const loadUser = async () => {
      const profile = await AuthService.getCurrentUser();
      setUser(profile);
    };
    loadUser();
  }, []);

  const handleLocationUpdate = useCallback((data: any) => {
    if (!data?.coords) return;
    setTrackedUsers(prev => ({
      ...prev,
      [data.id]: {
        id: data.id,
        name: data.name || 'Unknown',
        role: data.role || 'citizen',
        latitude: data.coords.latitude,
        longitude: data.coords.longitude,
        timestamp: data.timestamp || Date.now(),
      },
    }));
  }, []);

  const handleIncidentAssignment = useCallback((data: any) => {
    setAssignedIncident(data);
  }, []);

  useEffect(() => {
    SocketService.on('location_update', handleLocationUpdate);
    SocketService.on('incident_assignment', handleIncidentAssignment);

    // Mock an assignment for testing if role is responder
    if (user?.role === 'responder') {
      setTimeout(() => {
        setAssignedIncident({
          id: 'inc-99',
          title: 'Emergency: Flash Flood',
          latitude: 26.85,
          longitude: 80.95
        });
      }, 3000);
    }

    return () => {
      SocketService.off('location_update', handleLocationUpdate);
      SocketService.off('incident_assignment', handleIncidentAssignment);
    };
  }, [handleLocationUpdate, handleIncidentAssignment, user]);

  return (
    <View style={styles.container}>
      <MapView 
        style={styles.map} 
        initialRegion={initialRegion}
        showsUserLocation={true}
        showsMyLocationButton={true}
        userInterfaceStyle="dark"
      >
        {heatmapPoints.map((point, idx) => (
          <React.Fragment key={`heatmap-${idx}`}>
            <Circle
              center={{ latitude: point.lat, longitude: point.lon }}
              radius={point.radius}
              fillColor={point.type === 'incident' ? `rgba(255, 77, 77, ${point.intensity * 0.6})` : `rgba(255, 148, 77, ${point.intensity * 0.6})`}
              strokeColor={point.type === 'incident' ? 'rgba(255, 77, 77, 0.8)' : 'rgba(255, 148, 77, 0.8)'}
              strokeWidth={1}
            />
            <Marker coordinate={{ latitude: point.lat, longitude: point.lon }}>
              <View style={styles.markerContainer}>
                <Text style={styles.markerText}>{point.type === 'incident' ? '🔥' : '⚠️'} {point.label}</Text>
              </View>
            </Marker>
          </React.Fragment>
        ))}

        {assignedIncident && (
          <>
            <Marker 
              coordinate={{ latitude: assignedIncident.latitude, longitude: assignedIncident.longitude }}
            >
              <View style={[styles.markerContainer, { backgroundColor: 'red' }]}>
                <Text style={styles.markerText}>🚨 {assignedIncident.title}</Text>
              </View>
            </Marker>
            {routeCoordinates.length > 0 && (
              <Polyline
                coordinates={routeCoordinates}
                strokeWidth={5}
                strokeColor="#00d4ff"
              />
            )}
          </>
        )}

        {Object.values(trackedUsers).map(userLoc => (
          <Marker
            key={userLoc.id}
            coordinate={{ latitude: userLoc.latitude, longitude: userLoc.longitude }}
          >
            <View style={styles.userMarkerContainer}>
              <Text style={styles.userMarkerText}>
                {userLoc.role === 'responder' ? '🚑' : '🧍'} {userLoc.name.split(' ')[0] || 'User'}
              </Text>
            </View>
          </Marker>
        ))}
      </MapView>

      <View style={styles.overlay}>
        <ThemedText style={styles.overlayTitle}>
          {user?.role === 'responder' ? 'Responder Operational Map' : 'AI Predictive Risk Map'}
        </ThemedText>
        <ThemedText style={styles.overlayText}>
          Highlighted zones indicate high probability of incident spread based on live weather and historical data.
        </ThemedText>
        <ThemedText style={styles.overlayText}>
          Live markers show active {user?.role === 'responder' ? 'citizens/responders in the field.' : 'responders near your area.'}
        </ThemedText>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
  },
  map: {
    width: '100%',
    height: '100%',
  },
  markerContainer: {
    backgroundColor: 'rgba(0,0,0,0.7)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
  },
  markerText: {
    color: 'white',
    fontSize: 10,
    fontWeight: 'bold',
  },
  userMarkerContainer: {
    backgroundColor: 'rgba(0,0,0,0.7)',
    paddingHorizontal: 8,
    paddingVertical: 4,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: 'rgba(0,212,255,0.8)',
  },
  userMarkerText: {
    color: 'white',
    fontSize: 10,
    fontWeight: 'bold',
  },
  overlay: {
    position: 'absolute',
    bottom: 20,
    left: 20,
    right: 20,
    backgroundColor: 'rgba(20,20,20,0.85)',
    padding: 16,
    borderRadius: 12,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.2)',
  },
  overlayTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    marginBottom: 4,
    color: '#00d4ff',
  },
  overlayText: {
    fontSize: 12,
    color: 'rgba(255,255,255,0.7)',
  }
});
