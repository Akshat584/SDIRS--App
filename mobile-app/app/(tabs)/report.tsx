import React, { useState, useEffect } from 'react';
import { StyleSheet, TextInput, TouchableOpacity, ScrollView, Alert, View, Image, ActivityIndicator, Text } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { Ionicons } from '@expo/vector-icons';
import axios from 'axios';

import { ThemedText } from '@/components/themed-text';
import { useLocation } from '@/hooks/useLocation';
import SocketService from '@/services/socketService';
import { MLService, ImageAnalysisResult } from '@/services/mlService';
import { AuthService } from '@/services/authService';

import { API_BASE } from '@/services/apiConfig';
import SyncService from '@/services/syncService';

const INCIDENT_CATEGORIES = [
  { id: 'flood', label: 'Flood', icon: 'water', color: '#00d4ff' },
  { id: 'fire', label: 'Fire', icon: 'flame', color: '#ff3b3b' },
  { id: 'medical', label: 'Medical', icon: 'medical', color: '#ffcc00' },
  { id: 'earthquake', label: 'Earthquake', icon: 'pulse', color: '#8b5cf6' },
  { id: 'roadblock', label: 'Road Block', icon: 'warning', color: '#ff944d' },
] as const;

type IncidentCategory = typeof INCIDENT_CATEGORIES[number]['id'];

const SAFETY_ADVISORIES: Record<IncidentCategory, string[]> = {
  flood: ['Move to higher ground immediately.', 'Avoid walking or driving through flood waters.', 'Turn off utilities if instructed.'],
  fire: ['Evacuate the building immediately.', 'Stay low to the ground to avoid smoke.', 'Do not use elevators.'],
  medical: ['Do not move the person unless necessary.', 'Check for breathing and pulse.', 'Apply pressure to any bleeding.'],
  earthquake: ['Drop, Cover, and Hold on.', 'Stay away from windows and heavy furniture.', 'If outside, move to an open area.'],
  roadblock: ['Use alternative routes.', 'Do not attempt to bypass official barriers.', 'Watch for emergency responders.'],
};

export default function ReportScreen() {
  const { location } = useLocation();
  const [selectedCategory, setSelectedCategory] = useState<IncidentCategory | null>(null);
  const [description, setDescription] = useState('');

  // ML States
  const [imageUri, setImageUri] = useState<string | null>(null);
  const [isAnalyzingImage, setIsAnalyzingImage] = useState(false);
  const [edgeAnalysis, setEdgeAnalysis] = useState<ImageAnalysisResult | null>(null);
  const [cloudAnalysis, setCloudAnalysis] = useState<ImageAnalysisResult | null>(null);
  const [nlpSeverity, setNlpSeverity] = useState<'low' | 'medium' | 'high' | 'critical'>('low');
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Automatically calculate severity as the user types
  useEffect(() => {
    if (description.length > 5) {
      const severity = MLService.analyzeTextSeverity(description);
      setNlpSeverity(severity);
    } else {
      setNlpSeverity('low');
    }
  }, [description]);

  const pickImage = async () => {
    const result = await ImagePicker.launchImageLibraryAsync({
      mediaTypes: ['images'],
      allowsEditing: true,
      aspect: [4, 3],
      quality: 0.5,
    });

    if (!result.canceled && result.assets && result.assets.length > 0) {
      const uri = result.assets[0].uri;
      setImageUri(uri);

      setIsAnalyzingImage(true);
      try {
        // 1. Edge AI Triage (Instant, Zero-Bandwidth)
        const edgeRes = await MLService.performOnDeviceTriage(uri);
        setEdgeAnalysis(edgeRes);

        // Auto-select category based on Edge AI if it's high confidence
        const edgeLabel = edgeRes.detectedLabels[0]?.toLowerCase();
        const matchedCat = INCIDENT_CATEGORIES.find(c => edgeLabel?.includes(c.id));
        if (matchedCat) setSelectedCategory(matchedCat.id);

        // 2. Cloud AI Analysis (Deep Triage)
        const cloudRes = await MLService.analyzeImage(uri);
        setCloudAnalysis(cloudRes);

      } catch (error) {
        console.error('Analysis Failed', error);
      } finally {
        setIsAnalyzingImage(false);
      }
    }
  };

  const handleSubmit = async () => {
    if (!selectedCategory || !description) {
      Alert.alert('Incomplete Report', 'Please select a category and provide a description.');
      return;
    }

    if (!location) {
      Alert.alert('Location Required', 'We need your GPS location to send help.');
      return;
    }

    setIsSubmitting(true);

    try {
      const user = await AuthService.getCurrentUser();

      const reportData: any = {
        lat: location.coords.latitude.toString(),
        lon: location.coords.longitude.toString(),
        incident_type: selectedCategory,
        title: `Emergency: ${selectedCategory.toUpperCase()}`,
        description: description,
        reporter_id: user?.id?.toString() || '1',
      };

      const formData = new FormData();
      Object.keys(reportData).forEach(key => formData.append(key, reportData[key]));

      if (imageUri) {
        const uriParts = imageUri.split('.');
        const fileType = uriParts[uriParts.length - 1];
        const photo = {
          uri: imageUri,
          name: `photo.${fileType}`,
          type: `image/${fileType}`,
        } as any;
        formData.append('photo', photo);
        reportData.photo = photo;
      }

      try {
        const response = await axios.post(`${API_BASE}/api/incidents`, formData, {
          headers: { 'Content-Type': 'multipart/form-data' },
          timeout: 15000, 
        });

        if (response.data.status === 'success') {
          // Emit via socket for real-time dashboard update
          SocketService.emit('incident_reported', {
            id: response.data.incident_id,
            type: selectedCategory,
            location: location.coords,
            severity: nlpSeverity
          });

          Alert.alert(
            'Report Logged',
            'Responders have been notified. Please follow the safety instructions.',
            [{ text: 'OK', onPress: resetForm }]
          );
        }
      } catch (_submitError) {
        console.log('Network failure, queuing incident for offline sync');
        await SyncService.queueIncident(reportData);
        Alert.alert(
          'Offline Mode',
          'Network is unstable. Your report has been saved and will be sent automatically when connection is restored.',
          [{ text: 'OK', onPress: resetForm }]
        );
      }
    } catch (error) {
      console.error('Submission error:', error);
      Alert.alert('Error', 'Failed to submit report. Please try again.');
    } finally {
      setIsSubmitting(false);
    }
  };

  const resetForm = () => {
    setSelectedCategory(null);
    setDescription('');
    setImageUri(null);
    setEdgeAnalysis(null);
    setCloudAnalysis(null);
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical': return '#9b1a1a';
      case 'high': return '#ff3b3b';
      case 'medium': return '#ffcc00';
      default: return '#34c759';
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      <ThemedText type="subtitle" style={styles.label}>1. Select Incident Type</ThemedText>
      <View style={styles.categoryGrid}>
        {INCIDENT_CATEGORIES.map((cat) => (
          <TouchableOpacity
            key={cat.id}
            style={[
              styles.categoryItem,
              selectedCategory === cat.id && { borderColor: cat.color, backgroundColor: `${cat.color}20` }
            ]}
            onPress={() => setSelectedCategory(cat.id)}
          >
            <Ionicons name={cat.icon as any} size={24} color={selectedCategory === cat.id ? cat.color : '#8aa3b8'} />
            <Text style={[styles.categoryLabel, selectedCategory === cat.id && { color: cat.color }]}>
              {cat.label}
            </Text>
          </TouchableOpacity>
        ))}
      </View>

      <ThemedText type="subtitle" style={styles.label}>2. Capture Photo</ThemedText>
      <TouchableOpacity style={styles.imagePicker} onPress={pickImage}>
        {imageUri ? (
          <Image source={{ uri: imageUri }} style={styles.previewImage} />
        ) : (
          <View style={styles.imagePickerPlaceholder}>
            <Ionicons name="camera" size={32} color="rgba(255,255,255,0.5)" />
            <ThemedText style={styles.imagePickerText}>Add evidence (highly recommended)</ThemedText>
          </View>
        )}
      </TouchableOpacity>

      {isAnalyzingImage && (
        <View style={styles.analysisLoading}>
          <ActivityIndicator size="small" color="#00d4ff" />
          <ThemedText style={styles.analysisLoadingText}>AI Triage in progress...</ThemedText>
        </View>
      )}

      <View style={styles.aiResultContainer}>
        {edgeAnalysis && (
          <View style={[styles.mlCard, { borderColor: getSeverityColor(edgeAnalysis.severity) }]}>
            <View style={styles.aiBadge}>
              <Ionicons name="flash" size={10} color="#ffcc00" />
              <Text style={styles.aiBadgeText}>EDGE AI (OFFLINE)</Text>
            </View>
            <ThemedText style={{ fontSize: 12, fontWeight: 'bold' }}>TRIAGE: {edgeAnalysis.severity.toUpperCase()}</ThemedText>
            <ThemedText style={styles.mlText}>Confidence: {(edgeAnalysis.confidence * 100).toFixed(0)}%</ThemedText>
          </View>
        )}

        {cloudAnalysis && (
          <View style={[styles.mlCard, { borderColor: getSeverityColor(cloudAnalysis.severity), borderLeftColor: '#00d4ff' }]}>
            <View style={styles.aiBadge}>
              <Ionicons name="cloud-done" size={10} color="#00d4ff" />
              <Text style={styles.aiBadgeText}>CLOUD AI (VERIFIED)</Text>
            </View>
            <ThemedText style={{ fontSize: 12, fontWeight: 'bold' }}>ASSESSMENT: {cloudAnalysis.severity.toUpperCase()}</ThemedText>
            <ThemedText style={styles.mlText}>Damage details: {cloudAnalysis.detectedLabels.join(', ')}</ThemedText>
          </View>
        )}
      </View>

      <ThemedText type="subtitle" style={styles.label}>3. Describe the Situation</ThemedText>
      <TextInput
        style={[styles.input, styles.textArea]}
        placeholder="What's happening? Any victims? Specific location details?"
        placeholderTextColor="rgba(255,255,255,0.3)"
        multiline
        numberOfLines={4}
        value={description}
        onChangeText={setDescription}
      />

      {selectedCategory && SAFETY_ADVISORIES[selectedCategory] && (
        <View style={styles.advisoryCard}>
          <View style={styles.advisoryHeader}>
            <Ionicons name="shield-checkmark" size={18} color="#00ff9d" />
            <Text style={styles.advisoryTitle}> IMMEDIATE SAFETY INSTRUCTIONS</Text>
          </View>
          {SAFETY_ADVISORIES[selectedCategory].map((tip, idx) => (
            <Text key={idx} style={styles.advisoryTip}>• {tip}</Text>
          ))}
        </View>
      )}

      <TouchableOpacity
        style={[styles.submitButton, (isSubmitting || !selectedCategory) && { opacity: 0.5 }]}
        onPress={handleSubmit}
        disabled={isSubmitting || !selectedCategory}
      >
        {isSubmitting ? (
          <ActivityIndicator size="small" color="white" />
        ) : (
          <ThemedText style={styles.submitText}>Submit Emergency Report</ThemedText>
        )}
      </TouchableOpacity>

      <View style={styles.footer}>
        <Ionicons name="location" size={12} color="#00d4ff" />
        <Text style={styles.footerText}> Your GPS coordinates will be sent to the command center.</Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#070a0f' },
  content: { padding: 20, paddingBottom: 60 },
  label: { marginBottom: 12, marginTop: 20, fontSize: 14, color: '#8aa3b8', letterSpacing: 0.5 },
  categoryGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10 },
  categoryItem: {
    width: '31%',
    aspectRatio: 1,
    backgroundColor: '#1a1f26',
    borderRadius: 12,
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'transparent',
  },
  categoryLabel: { fontSize: 10, marginTop: 8, color: '#8aa3b8', fontWeight: 'bold' },
  imagePicker: {
    height: 160,
    backgroundColor: '#1a1f26',
    borderRadius: 12,
    overflow: 'hidden',
    justifyContent: 'center',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.05)',
  },
  imagePickerPlaceholder: { alignItems: 'center', gap: 8 },
  imagePickerText: { color: 'rgba(255,255,255,0.4)', fontSize: 12 },
  previewImage: { width: '100%', height: '100%' },
  input: {
    backgroundColor: '#1a1f26',
    borderRadius: 12,
    padding: 16,
    color: 'white',
    fontSize: 15,
  },
  textArea: { height: 100, textAlignVertical: 'top' },
  mlCard: {
    marginTop: 10,
    padding: 10,
    backgroundColor: 'rgba(255,255,255,0.02)',
    borderRadius: 8,
    borderLeftWidth: 3,
  },
  mlText: { fontSize: 11, color: '#8aa3b8', marginTop: 2 },
  aiResultContainer: { marginTop: 10, gap: 10 },
  aiBadge: { flexDirection: 'row', alignItems: 'center', gap: 4, marginBottom: 4 },
  aiBadgeText: { fontSize: 8, fontWeight: '900', color: '#8aa3b8' },
  analysisLoading: { flexDirection: 'row', alignItems: 'center', gap: 8, marginTop: 10, justifyContent: 'center' },
  analysisLoadingText: { fontSize: 12, color: '#00d4ff' },
  advisoryCard: {
    marginTop: 24,
    padding: 16,
    backgroundColor: 'rgba(0, 255, 157, 0.05)',
    borderRadius: 12,
    borderWidth: 1,
    borderColor: 'rgba(0, 255, 157, 0.2)',
  },
  advisoryHeader: { flexDirection: 'row', alignItems: 'center', marginBottom: 10 },
  advisoryTitle: { color: '#00ff9d', fontSize: 12, fontWeight: 'bold' },
  advisoryTip: { color: '#e8f4fd', fontSize: 12, marginBottom: 4, lineHeight: 18 },
  submitButton: {
    backgroundColor: '#ff3b3b',
    padding: 18,
    borderRadius: 12,
    alignItems: 'center',
    marginTop: 30,
    shadowColor: '#ff3b3b',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 5,
  },
  submitText: { color: 'white', fontWeight: 'bold', fontSize: 16, letterSpacing: 1 },
  footer: { flexDirection: 'row', justifyContent: 'center', alignItems: 'center', marginTop: 20 },
  footerText: { fontSize: 10, color: 'rgba(255,255,255,0.3)' },
});
