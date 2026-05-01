import React, { useState } from 'react';
import { StyleSheet, TextInput, TouchableOpacity, View, ActivityIndicator, Alert, KeyboardAvoidingView, Platform, ScrollView } from 'react-native';
import { useRouter } from 'expo-router';

import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import { IconSymbol } from '@/components/ui/icon-symbol';
import { AuthService, UserRole } from '@/services/authService';

export default function AuthScreen() {
  const router = useRouter();
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [role, setRole] = useState<UserRole>('citizen');
  const [loading, setLoading] = useState(false);

  const handleAuth = async () => {
    if (!email || !password || (!isLogin && !fullName)) {
      Alert.alert('Missing Info', 'Please fill in all fields.');
      return;
    }

    setLoading(true);
    if (isLogin) {
      const { error } = await AuthService.signIn(email, password);
      if (error) {
        Alert.alert('Login Failed', error);
      } else {
        router.replace('/(tabs)' as any);
      }
    } else {
      const { error } = await AuthService.signUp(email, password, fullName, role);
      if (error) {
        Alert.alert('Signup Failed', error);
      } else {
        Alert.alert('Success', 'Check your email for confirmation!');
        setIsLogin(true);
      }
    }
    setLoading(false);
  };

  return (
    <KeyboardAvoidingView 
      behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
      style={styles.container}
    >
      <ScrollView contentContainerStyle={styles.scrollContent}>
        <ThemedView style={styles.header}>
          <IconSymbol name="exclamationmark.shield.fill" size={64} color="#ff3b3b" />
          <ThemedText type="title" style={styles.title}>Disaster Response</ThemedText>
          <ThemedText style={styles.subtitle}>
            {isLogin ? 'Welcome back, stay safe.' : 'Join the network, save lives.'}
          </ThemedText>
        </ThemedView>

        <ThemedView style={styles.form}>
          {!isLogin && (
            <>
              <ThemedText style={styles.label}>Full Name</ThemedText>
              <TextInput
                style={styles.input}
                placeholder="John Doe"
                placeholderTextColor="rgba(255,255,255,0.3)"
                value={fullName}
                onChangeText={setFullName}
              />
              
              <ThemedText style={styles.label}>Select Your Role</ThemedText>
              <View style={styles.roleContainer}>
                <TouchableOpacity 
                  style={[styles.roleButton, role === 'citizen' && styles.roleButtonActive]}
                  onPress={() => setRole('citizen')}
                >
                  <ThemedText style={[styles.roleText, role === 'citizen' && styles.roleTextActive]}>Citizen</ThemedText>
                </TouchableOpacity>
                <TouchableOpacity 
                  style={[styles.roleButton, role === 'responder' && styles.roleButtonActive]}
                  onPress={() => setRole('responder')}
                >
                  <ThemedText style={[styles.roleText, role === 'responder' && styles.roleTextActive]}>First Responder</ThemedText>
                </TouchableOpacity>
              </View>
            </>
          )}

          <ThemedText style={styles.label}>Email Address</ThemedText>
          <TextInput
            style={styles.input}
            placeholder="email@example.com"
            placeholderTextColor="rgba(255,255,255,0.3)"
            autoCapitalize="none"
            keyboardType="email-address"
            value={email}
            onChangeText={setEmail}
          />

          <ThemedText style={styles.label}>Password</ThemedText>
          <TextInput
            style={styles.input}
            placeholder="••••••••"
            placeholderTextColor="rgba(255,255,255,0.3)"
            secureTextEntry
            value={password}
            onChangeText={setPassword}
          />

          <TouchableOpacity 
            style={[styles.authButton, loading && { opacity: 0.7 }]} 
            onPress={handleAuth}
            disabled={loading}
          >
            {loading ? <ActivityIndicator color="white" /> : (
              <ThemedText style={styles.authButtonText}>{isLogin ? 'Login' : 'Create Account'}</ThemedText>
            )}
          </TouchableOpacity>

          <TouchableOpacity 
            style={styles.switchButton} 
            onPress={() => setIsLogin(!isLogin)}
          >
            <ThemedText style={styles.switchText}>
              {isLogin ? "Don't have an account? Sign Up" : "Already have an account? Login"}
            </ThemedText>
          </TouchableOpacity>
        </ThemedView>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#151718',
  },
  scrollContent: {
    padding: 24,
    paddingTop: 80,
  },
  header: {
    alignItems: 'center',
    marginBottom: 40,
    backgroundColor: 'transparent',
  },
  title: {
    marginTop: 16,
    fontSize: 28,
  },
  subtitle: {
    opacity: 0.6,
    marginTop: 8,
  },
  form: {
    backgroundColor: 'rgba(255,255,255,0.05)',
    padding: 20,
    borderRadius: 16,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
  },
  label: {
    fontSize: 14,
    fontWeight: '600',
    marginBottom: 8,
    marginTop: 16,
  },
  input: {
    backgroundColor: 'rgba(0,0,0,0.3)',
    borderRadius: 8,
    padding: 12,
    color: 'white',
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.1)',
  },
  roleContainer: {
    flexDirection: 'row',
    gap: 12,
    marginBottom: 8,
  },
  roleButton: {
    flex: 1,
    padding: 10,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: 'rgba(255,255,255,0.2)',
    alignItems: 'center',
  },
  roleButtonActive: {
    backgroundColor: '#ff3b3b',
    borderColor: '#ff3b3b',
  },
  roleText: {
    fontSize: 12,
    fontWeight: 'bold',
    color: 'rgba(255,255,255,0.6)',
  },
  roleTextActive: {
    color: 'white',
  },
  authButton: {
    backgroundColor: '#ff3b3b',
    padding: 16,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 32,
  },
  authButtonText: {
    color: 'white',
    fontWeight: 'bold',
    fontSize: 16,
  },
  switchButton: {
    marginTop: 20,
    alignItems: 'center',
  },
  switchText: {
    color: '#00d4ff',
    fontSize: 14,
  },
});
