// SDIRS Edge AI Machine Learning Service (Module 3 - Edge Triage)
// This service simulates on-device image verification using TensorFlow Lite.

export interface ImageAnalysisResult {
  detectedLabels: string[];
  severity: 'low' | 'medium' | 'high' | 'critical';
  confidence: number;
}

/**
 * TFLiteEngine: Mock for actual TFLite native module usage in React Native.
 * In a real app, you would use: import Tflite from 'react-native-tflite';
 * Or for Expo: import * as tf from '@tensorflow/tfjs';
 */
const TFLiteEngine = {
  loadModel: async (modelPath: string, labelsPath: string) => {
    console.log(`[Edge AI] Loading model from ${modelPath}...`);
    // Simulating native module TFLite model loading
    return true;
  },
  
  runInference: async (imageUri: string): Promise<any> => {
    console.log(`[Edge AI] Running on-device triage for: ${imageUri}`);
    // Simulated inference logic
    const labels = ['fire', 'flood', 'debris', 'structure_damage', 'road_blocked', 'medical'];
    const count = Math.floor(Math.random() * 3) + 1;
    const detected = [];
    for(let i=0; i<count; i++) {
        detected.push(labels[Math.floor(Math.random() * labels.length)]);
    }
    return detected;
  }
};

export const MLService = {
  /**
   * TASK 1: Edge-AI Verification (Module 3)
   * TensorFlow Lite on-device image triage (Zero-Bandwidth)
   * This logic runs locally on the mobile device without hitting the server.
   */
  performOnDeviceTriage: async (imageUri: string): Promise<ImageAnalysisResult> => {
    console.info("SDIRS: Initializing on-device Edge AI triage...");
    
    // Simulate model loading (usually happens once at startup)
    await TFLiteEngine.loadModel(
      'assets/models/disaster_triage_v1.tflite',
      'assets/models/labels.txt'
    );

    // Artificial delay to simulate TFLite inference processing
    await new Promise(r => setTimeout(r, 800));

    const detectedLabels = await TFLiteEngine.runInference(imageUri);
    
    // Determine severity locally based on detected disaster features
    let severity: 'low' | 'medium' | 'high' | 'critical' = 'low';
    if (detectedLabels.includes('fire') || detectedLabels.includes('trapped')) {
      severity = 'critical';
    } else if (detectedLabels.includes('flood') || detectedLabels.includes('structure_damage')) {
      severity = 'high';
    } else if (detectedLabels.includes('road_blocked') || detectedLabels.includes('debris')) {
      severity = 'medium';
    }

    const result: ImageAnalysisResult = {
      detectedLabels,
      severity,
      confidence: 0.88 + (Math.random() * 0.08)
    };

    console.log(`[Edge AI Result] Verified on-device: ${JSON.stringify(result)}`);
    return result;
  },

  /**
   * Original analyzeImage (Simulates cloud/server analysis for comparison or fallback)
   */
  analyzeImage: async (imageUri: string): Promise<ImageAnalysisResult> => {
    return new Promise((resolve) => {
      setTimeout(() => {
        const scenarios = [
          { labels: ['fire', 'smoke', 'structure damage'], severity: 'critical' as const },
          { labels: ['flood', 'water', 'submerged vehicle'], severity: 'high' as const },
          { labels: ['fallen tree', 'debris', 'blocked road'], severity: 'medium' as const },
          { labels: ['puddle', 'rain'], severity: 'low' as const },
        ];
        const result = scenarios[Math.floor(Math.random() * scenarios.length)];
        
        resolve({
          detectedLabels: result.labels,
          severity: result.severity,
          confidence: 0.85 + (Math.random() * 0.1),
        });
      }, 2000);
    });
  },

  /**
   * TASK 2: NLP for Incident Classification
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
