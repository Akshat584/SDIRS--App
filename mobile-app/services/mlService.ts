// SDIRS Edge AI Machine Learning Service (Module 3 - Edge Triage)
// This service simulates on-device image verification using TensorFlow Lite.

import axios from 'axios';
import { API_BASE } from './apiConfig';

export interface ImageAnalysisResult {
  detectedLabels: string[];
  severity: 'low' | 'medium' | 'high' | 'critical';
  confidence: number;
  verified: boolean;
}

export const MLService = {
  /**
   * TASK 1: Intelligent Incident Analysis
   * Calls the SDIRS Backend AI pipeline for CV and Severity prediction.
   */
  analyzeImage: async (imageUri: string, description: string = "", latitude: number = 0, longitude: number = 0): Promise<ImageAnalysisResult> => {
    try {
      console.log(`[ML Service] Requesting cloud analysis for: ${imageUri}`);
      
      const response = await axios.post(`${API_BASE}/api/analysis/analyze`, {
        description: description,
        image_uri: imageUri,
        latitude: latitude,
        longitude: longitude
      });

      const { severity, verified, ml_labels } = response.data;

      return {
        detectedLabels: ml_labels,
        severity: severity as any,
        confidence: 0.9, // Backend handles confidence thresholding
        verified: verified
      };
    } catch (error) {
      console.error('[ML Service] Cloud analysis failed, using local fallback:', error);
      // Fallback to local rule-based analysis if server is unreachable
      const localSeverity = MLService.analyzeTextSeverity(description);
      return {
        detectedLabels: ['offline_mode'],
        severity: localSeverity,
        confidence: 0.5,
        verified: false
      };
    }
  },

  /**
   * performOnDeviceTriage: Optimized for low-bandwidth environments.
   * Currently redirects to analyzeImage as a cloud-first strategy for this phase.
   */
  performOnDeviceTriage: async (imageUri: string, description: string = ""): Promise<ImageAnalysisResult> => {
    return MLService.analyzeImage(imageUri, description);
  },

  /**
   * TASK 2: NLP for Incident Classification (Local Fallback)
   */
  analyzeTextSeverity: (description: string): 'low' | 'medium' | 'high' | 'critical' => {
    const text = description.toLowerCase();
    const criticalKeywords = ['trapped', 'explosion', 'bleeding', 'unconscious', 'dying', 'building collapsed'];
    const highKeywords = ['fire', 'flood', 'fast water', 'burning', 'evacuate', 'casualty'];
    const mediumKeywords = ['blocked', 'tree down', 'no power', 'broken glass', 'accident'];
    
    if (criticalKeywords.some(kw => text.includes(kw))) return 'critical';
    if (highKeywords.some(kw => text.includes(kw))) return 'high';
    if (mediumKeywords.some(kw => text.includes(kw))) return 'medium';
    
    return 'low';
  },

  /**
   * TASK 4: Crowd-Sourced Data Verification
   */
  verifyIncident: async (type: string, coordinates: { latitude: number, longitude: number } | undefined): Promise<{ verified: boolean, confidenceScore: number, similarReports: number }> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        if (!coordinates) {
          return resolve({ verified: false, confidenceScore: 30, similarReports: 0 });
        }
        const similarReports = Math.floor(Math.random() * 5); 
        const verified = similarReports > 1;
        const confidenceScore = verified ? 85 + (similarReports * 2) : 40;
        resolve({ verified, confidenceScore, similarReports });
      }, 1000);
    });
  }
};
