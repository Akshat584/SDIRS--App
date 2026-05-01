import React from 'react';
import { View, Text, StyleSheet } from 'react-native';

// Web fallback components for react-native-maps
// react-native-maps only supports native iOS/Android platforms

interface Region {
  latitude: number;
  longitude: number;
  latitudeDelta: number;
  longitudeDelta: number;
}

interface MapViewProps {
  style?: any;
  initialRegion?: Region;
  showsUserLocation?: boolean;
  showsMyLocationButton?: boolean;
  userInterfaceStyle?: string;
  children?: React.ReactNode;
}

interface MarkerProps {
  coordinate: { latitude: number; longitude: number };
  children?: React.ReactNode;
  key?: string;
}

interface CircleProps {
  center: { latitude: number; longitude: number };
  radius: number;
  fillColor?: string;
  strokeColor?: string;
  strokeWidth?: number;
}

interface PolylineProps {
  coordinates: { latitude: number; longitude: number }[];
  strokeWidth?: number;
  strokeColor?: string;
}

function MapViewWeb({ style, initialRegion, children }: MapViewProps) {
  const lat = initialRegion?.latitude ?? 26.8467;
  const lon = initialRegion?.longitude ?? 80.9462;

  return (
    <View style={[styles.container, style]}>
      <iframe
        title="Map"
        width="100%"
        height="100%"
        style={{ border: 0 }}
        src={`https://www.openstreetmap.org/export/embed.html?bbox=${lon - 0.05}%2C${lat - 0.05}%2C${lon + 0.05}%2C${lat + 0.05}&layer=mapnik&marker=${lat}%2C${lon}`}
      />
      <View style={styles.webBanner}>
        <Text style={styles.bannerText}>
          📱 For full map features, use the native mobile app
        </Text>
      </View>
    </View>
  );
}

// Stub components that render nothing on web
function MarkerWeb({ children }: MarkerProps) {
  return null;
}

function CircleWeb(_props: CircleProps) {
  return null;
}

function PolylineWeb(_props: PolylineProps) {
  return null;
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#1a1a2e',
  },
  webBanner: {
    position: 'absolute',
    top: 10,
    left: 10,
    right: 10,
    backgroundColor: 'rgba(0,0,0,0.75)',
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: 'rgba(0,212,255,0.4)',
  },
  bannerText: {
    color: '#00d4ff',
    fontSize: 12,
    textAlign: 'center',
  },
});

export default MapViewWeb;
export { MarkerWeb as Marker, CircleWeb as Circle, PolylineWeb as Polyline };
