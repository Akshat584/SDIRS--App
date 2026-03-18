import React, { useState, useEffect, useRef } from 'react';
import { StyleSheet, View, Text, TextInput, TouchableOpacity, FlatList, KeyboardAvoidingView, Platform } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import { Ionicons } from '@expo/vector-icons';

import { ThemedText } from '@/components/themed-text';
import { ThemedView } from '@/components/themed-view';
import SocketService from '@/services/socketService';
import { AuthService, UserProfile } from '@/services/authService';

interface ChatMessage {
  id: string;
  sender_id: string;
  sender_name?: string;
  text: string;
  type: 'chat' | 'broadcast' | 'command';
  timestamp: number;
}

export default function MessagesScreen() {
  const insets = useSafeAreaInsets();
  const [user, setUser] = useState<UserProfile | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputText, setInputText] = useState('');
  const flatListRef = useRef<FlatList>(null);

  useEffect(() => {
    const loadUser = async () => {
      const profile = await AuthService.getCurrentUser();
      setUser(profile);
    };
    loadUser();

    // Listen for incoming messages
    SocketService.on('receive_message', (data: any) => {
      const newMessage: ChatMessage = {
        id: Math.random().toString(36).substr(2, 9),
        sender_id: data.sender_id,
        sender_name: data.sender_name || 'System',
        text: data.text,
        type: data.type || 'chat',
        timestamp: Date.now(),
      };
      setMessages(prev => [...prev, newMessage]);
    });

    return () => {
      SocketService.off('receive_message', () => {});
    };
  }, []);

  const sendMessage = () => {
    if (!inputText.trim() || !user) return;

    const messageData = {
      sender_id: user.id,
      sender_name: user.fullName,
      text: inputText.trim(),
      type: 'chat',
    };

    SocketService.sendMessage(messageData);
    setInputText('');
  };

  const renderItem = ({ item }: { item: ChatMessage }) => {
    const isMe = item.sender_id === user?.id;
    const isBroadcast = item.type === 'broadcast';

    if (isBroadcast) {
      return (
        <View style={styles.broadcastContainer}>
          <View style={styles.broadcastBadge}>
            <Ionicons name="megaphone" size={12} color="white" />
            <Text style={styles.broadcastText}> EMERGENCY BROADCAST</Text>
          </View>
          <Text style={styles.broadcastMessage}>{item.text}</Text>
        </View>
      );
    }

    return (
      <View style={[styles.messageBubble, isMe ? styles.myMessage : styles.theirMessage]}>
        {!isMe && <Text style={styles.senderName}>{item.sender_name}</Text>}
        <Text style={styles.messageText}>{item.text}</Text>
        <Text style={styles.timestamp}>{new Date(item.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</Text>
      </View>
    );
  };

  return (
    <ThemedView style={[styles.container, { paddingBottom: insets.bottom }]}>
      <View style={styles.header}>
        <ThemedText type="subtitle">Communication Channel</ThemedText>
        <Text style={styles.channelStatus}>● SECURE SDIRS LINE</Text>
      </View>

      <FlatList
        ref={flatListRef}
        data={messages}
        keyExtractor={item => item.id}
        renderItem={renderItem}
        contentContainerStyle={styles.listContent}
        onContentSizeChange={() => flatListRef.current?.scrollToEnd()}
      />

      <KeyboardAvoidingView
        behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
        keyboardVerticalOffset={100}
      >
        <View style={styles.inputContainer}>
          <TextInput
            style={styles.input}
            value={inputText}
            onChangeText={setInputText}
            placeholder="Type a message..."
            placeholderTextColor="#888"
          />
          <TouchableOpacity style={styles.sendButton} onPress={sendMessage}>
            <Ionicons name="send" size={20} color="white" />
          </TouchableOpacity>
        </View>
      </KeyboardAvoidingView>
    </ThemedView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#070a0f',
  },
  header: {
    padding: 16,
    borderBottomWidth: 1,
    borderBottomColor: 'rgba(255,255,255,0.1)',
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  channelStatus: {
    fontSize: 10,
    color: '#00ff9d',
    fontWeight: 'bold',
  },
  listContent: {
    padding: 16,
  },
  messageBubble: {
    maxWidth: '80%',
    padding: 12,
    borderRadius: 16,
    marginBottom: 12,
  },
  myMessage: {
    alignSelf: 'flex-end',
    backgroundColor: '#00d4ff',
    borderBottomRightRadius: 4,
  },
  theirMessage: {
    alignSelf: 'flex-start',
    backgroundColor: '#1a1f26',
    borderBottomLeftRadius: 4,
  },
  senderName: {
    fontSize: 10,
    color: '#8aa3b8',
    marginBottom: 4,
    fontWeight: 'bold',
  },
  messageText: {
    color: 'white',
    fontSize: 14,
  },
  timestamp: {
    fontSize: 9,
    color: 'rgba(255,255,255,0.5)',
    alignSelf: 'flex-end',
    marginTop: 4,
  },
  broadcastContainer: {
    backgroundColor: 'rgba(155, 26, 26, 0.2)',
    borderWidth: 1,
    borderColor: '#9b1a1a',
    borderRadius: 8,
    padding: 12,
    marginBottom: 16,
  },
  broadcastBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#9b1a1a',
    alignSelf: 'flex-start',
    paddingHorizontal: 6,
    paddingVertical: 2,
    borderRadius: 4,
    marginBottom: 8,
  },
  broadcastText: {
    color: 'white',
    fontSize: 9,
    fontWeight: 'bold',
  },
  broadcastMessage: {
    color: 'white',
    fontSize: 14,
    fontWeight: '500',
  },
  inputContainer: {
    flexDirection: 'row',
    padding: 12,
    borderTopWidth: 1,
    borderTopColor: 'rgba(255,255,255,0.1)',
    alignItems: 'center',
  },
  input: {
    flex: 1,
    backgroundColor: '#1a1f26',
    borderRadius: 20,
    paddingHorizontal: 16,
    paddingVertical: 8,
    color: 'white',
    marginRight: 8,
  },
  sendButton: {
    backgroundColor: '#00d4ff',
    width: 40,
    height: 40,
    borderRadius: 20,
    justifyContent: 'center',
    alignItems: 'center',
  },
});
