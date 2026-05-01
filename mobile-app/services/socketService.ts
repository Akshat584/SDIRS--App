import { io, Socket } from 'socket.io-client';
import { API_CONFIG } from './apiConfig';

class SocketService {
  private socket: Socket | null = null;
  private readonly socketUrl = API_CONFIG.SOCKET_URL;

  /**
   * Initializes the socket connection.
   */
  connect() {
    if (this.socket) return;

    console.log(`[SocketService] Initializing socket connection to: ${this.socketUrl}`);

    this.socket = io(this.socketUrl, {
      transports: ['websocket'],
      autoConnect: true,
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionAttempts: 10,
      timeout: 20000,
    });

    this.socket.on('connect', () => {
      console.log('[SocketService] Connected:', this.socket?.id);
    });

    this.socket.on('connect_error', (error) => {
      console.error('[SocketService] Connection error:', error.message);
    });

    this.socket.on('disconnect', (reason) => {
      console.log('[SocketService] Disconnected:', reason);
    });

    this.socket.on('error', (error) => {
      console.error('[SocketService] Socket error:', error);
    });
  }

  /**
   * Listen for specific events from the server.
   */
  on(event: string, callback: (data: any) => void) {
    this.connect();
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
   */
  emit(event: string, data: any) {
    this.connect();
    this.socket?.emit(event, data);
  }

  /**
   * Send a chat message or broadcast.
   */
  sendMessage(messageData: {
    sender_id: string | number;
    sender_name?: string;
    incident_id?: number;
    text: string;
    type: string;
  }) {
    this.emit('send_message', messageData);
  }

  /**
   * Disconnects the socket.
   */
  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
      console.log('[SocketService] Socket disconnected and cleaned up');
    }
  }

  /**
   * Check if socket is connected.
   */
  isConnected(): boolean {
    return this.socket?.connected || false;
  }

  /**
   * Get the current socket ID.
   */
  getSocketId(): string | null {
    return this.socket?.id || null;
  }
}

export default new SocketService();
