import React, { useState, useEffect } from 'react';
import { StyleSheet, View, Text, ScrollView, TouchableOpacity, Alert, ActivityIndicator } from 'react-native';
import { Colors } from '@/constants/theme';
import { StatusCard } from '@/components/StatusCard';
import { CommonButton } from '@/components/CommonButton';
import axios from 'axios';
import { API_BASE_URL } from '@/services/apiConfig';
import * as Location from 'expo-location';

export default function SafetyScreen() {
  const [status, setStatus] = useState<'safe' | 'needs_help' | 'unknown'>('unknown');
  const [loading, setLoading] = useState(false);
  const [threatType, setThreatType] = useState('Flood'); // Default for demo
  const [manual, setManual] = useState<{checklist: string[], first_aid: string[]} | null>(null);

  useEffect(() => {
    fetchManual();
  }, [threatType]);

  const fetchManual = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/preparedness/manual/${threatType}`);
      setManual(response.data);
    } catch (error) {
      console.error('Error fetching manual:', error);
    }
  };

  const markSafe = async (isSafe: boolean) => {
    setLoading(true);
    try {
      let location = null;
      const { status } = await Location.requestForegroundPermissionsAsync();
      if (status === 'granted') {
        location = await Location.getCurrentPositionAsync({});
      }

      await axios.post(`${API_BASE_URL}/safety/check-in`, {
        status: isSafe ? 'safe' : 'needs_help',
        latitude: location?.coords.latitude,
        longitude: location?.coords.longitude,
        message: isSafe ? "I am okay." : "I need immediate assistance!"
      });

      setStatus(isSafe ? 'safe' : 'needs_help');
      Alert.alert(isSafe ? 'Safe' : 'Alert Sent', isSafe ? 'You have been marked as safe.' : 'Responders have been notified of your location.');
    } catch (error) {
      Alert.alert('Error', 'Could not update status. Check your connection.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container}>
      <View style={styles.header}>
        <Text style={styles.headerTitle}>SDIRS Safety Check</Text>
        <Text style={styles.headerSubtitle}>Mark yourself safe for family and responders</Text>
      </View>

      <View style={styles.statusSection}>
        <Text style={styles.sectionTitle}>Your Status</Text>
        <View style={[styles.statusIndicator, { backgroundColor: status === 'safe' ? '#2ecc71' : status === 'needs_help' ? '#e74c3c' : '#95a5a6' }]}>
          <Text style={styles.statusText}>{status.toUpperCase().replace('_', ' ')}</Text>
        </View>

        <View style={styles.buttonRow}>
          <TouchableOpacity 
            style={[styles.actionButton, { backgroundColor: '#2ecc71' }]} 
            onPress={() => markSafe(true)}
            disabled={loading}
          >
            <Text style={styles.buttonLabel}>I'M SAFE</Text>
          </TouchableOpacity>
          <TouchableOpacity 
            style={[styles.actionButton, { backgroundColor: '#e74c3c' }]} 
            onPress={() => markSafe(false)}
            disabled={loading}
          >
            <Text style={styles.buttonLabel}>NEED HELP</Text>
          </TouchableOpacity>
        </View>
        {loading && <ActivityIndicator size="small" color="#000" style={{marginTop: 10}} />}
      </View>

      <View style={styles.manualSection}>
        <Text style={styles.sectionTitle}>Preparedness Manual: {threatType}</Text>
        
        {manual ? (
          <>
            <Text style={styles.subsectionTitle}>✅ Checklist</Text>
            {manual.checklist.map((item, index) => (
              <View key={index} style={styles.manualItem}>
                <Text style={styles.manualText}>• {item}</Text>
              </View>
            ))}

            <Text style={styles.subsectionTitle}>🚑 First Aid</Text>
            {manual.first_aid.map((item, index) => (
              <View key={index} style={styles.manualItem}>
                <Text style={styles.manualText}>• {item}</Text>
              </View>
            ))}
          </>
        ) : (
          <Text>Loading manual...</Text>
        )}
      </View>

      <View style={styles.threatSelector}>
        <Text style={styles.smallLabel}>Change Manual Type:</Text>
        <ScrollView horizontal showsHorizontalScrollIndicator={false}>
          {['Flood', 'Fire', 'Earthquake'].map((t) => (
            <TouchableOpacity key={t} onPress={() => setThreatType(t)} style={styles.chip}>
              <Text style={{color: threatType === t ? '#3498db' : '#333'}}>{t}</Text>
            </TouchableOpacity>
          ))}
        </ScrollView>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#f8f9fa', padding: 20 },
  header: { marginBottom: 30, marginTop: 20 },
  headerTitle: { fontSize: 24, fontWeight: 'bold', color: '#2c3e50' },
  headerSubtitle: { fontSize: 14, color: '#7f8c8d', marginTop: 5 },
  statusSection: { backgroundColor: '#fff', padding: 20, borderRadius: 12, elevation: 2, marginBottom: 20 },
  sectionTitle: { fontSize: 18, fontWeight: '600', marginBottom: 15, color: '#34495e' },
  statusIndicator: { padding: 10, borderRadius: 8, alignItems: 'center', marginBottom: 20 },
  statusText: { color: '#fff', fontWeight: 'bold', fontSize: 16 },
  buttonRow: { flexDirection: 'row', justifyContent: 'space-between' },
  actionButton: { flex: 0.48, padding: 15, borderRadius: 10, alignItems: 'center' },
  buttonLabel: { color: '#fff', fontWeight: 'bold' },
  manualSection: { backgroundColor: '#fff', padding: 20, borderRadius: 12, elevation: 2, marginBottom: 20 },
  subsectionTitle: { fontSize: 16, fontWeight: 'bold', marginTop: 15, marginBottom: 10 },
  manualItem: { marginBottom: 8, paddingLeft: 5 },
  manualText: { fontSize: 14, lineHeight: 22, color: '#2c3e50' },
  threatSelector: { marginBottom: 40 },
  smallLabel: { fontSize: 12, color: '#7f8c8d', marginBottom: 10 },
  chip: { paddingHorizontal: 15, paddingVertical: 8, backgroundColor: '#eee', borderRadius: 20, marginRight: 10 }
});
