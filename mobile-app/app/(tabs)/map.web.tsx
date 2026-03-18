import React from 'react';
import { StyleSheet, View } from 'react-native';
import { ThemedText } from '@/components/themed-text';
import { IconSymbol } from '@/components/ui/icon-symbol';

export default function MapScreen() {
  return (
    <View style={styles.container}>
      <View style={styles.overlay}>
        <IconSymbol name="map.fill" size={64} color="rgba(255,255,255,0.2)" />
        <ThemedText style={styles.overlayTitle}>Map View Unavailable</ThemedText>
        <ThemedText style={styles.overlayText}>
          The interactive predictive risk map requires native capabilities and is currently only supported on the mobile application (iOS and Android).
        </ThemedText>
        <ThemedText style={[styles.overlayText, { marginTop: 12, color: '#00d4ff' }]}>
          Please install the Expo Go app on your phone and scan the QR code to access this feature.
        </ThemedText>
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#151718', // Consistent with app theme
  },
  overlay: {
    backgroundColor: 'rgba(20,20,20,0.85)',
    padding: 32,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
    margin: 24,
    alignItems: 'center',
    maxWidth: 400,
  },
  overlayTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    marginBottom: 12,
    marginTop: 16,
    color: '#ff3b3b',
    textAlign: 'center',
  },
  overlayText: {
    fontSize: 15,
    color: 'rgba(255,255,255,0.7)',
    textAlign: 'center',
    lineHeight: 22,
  }
});
