import { io, Socket } from 'socket.io-client';

// Define the URL for your backend server. 
// EXPO_PUBLIC_SOCKET_URL should be set in .env. 
// For local dev, this is typically your machine's IP (e.g., http://192.168.1.XX:3000) 
// or http://localhost:3000 for web/simulators.
const SOCKET_URL = process.env.EXPO_PUBLIC_SOCKET_URL || 'http://localhost:3000';

if (!process.env.EXPO_PUBLIC_SOCKET_URL) {
  console.warn(`[SocketService] EXPO_PUBLIC_SOCKET_URL not found in .env. Falling back to: ${SOCKET_URL}`);
}

class SocketService {
  private socket: Socket | null = null;

  /**
   * Initializes the socket connection.
   */
  connect() {
    if (this.socket) return;

    this.socket = io(SOCKET_URL, {
      transports: ['websocket'],
      autoConnect: true,
    });

    this.socket.on('connect', () => {
      console.log('Connected to Alert Server:', this.socket?.id);
    });

    this.socket.on('disconnect', () => {
      console.log('Disconnected from Alert Server');
    });

    this.socket.on('error', (error) => {
      console.error('Socket Error:', error);
    });
  }

  /**
   * Listen for specific events from the server.
   * @param event The event name (e.g., 'emergency_alert').
   * @param callback Function to handle the received data.
   */
  on(event: string, callback: (data: any) => void) {
    if (!this.socket) this.connect();
    this.socket?.on(event, callback);
  }

  /**
   * Remove a listener for a specific event.
   */
  off(event: string, callback: (data: any) => void) {
    this.socket?.off(event, callback);
  }

  /**
   * Emit events to the server.
   * @param event The event name (e.g., 'report_incident').
   * @param data The data to send.
   */
  emit(event: string, data: any) {
    if (!this.socket) this.connect();
    this.socket?.emit(event, data);
  }

  /**
   * Send a chat message or broadcast (Module 9).
   */
  sendMessage(messageData: { sender_id: string, incident_id?: number, text: string, type: string }) {
    this.emit('send_message', messageData);
  }

  /**
   * Disconnects the socket.
   */
  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }
}

export default new SocketService();
