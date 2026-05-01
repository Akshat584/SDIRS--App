// SDIRS Offline Resilience (Module 9)
// Robust Peer-to-Peer Communication Service using BLE Mesh principles.
// This implementation handles message propagation, relaying, and loop prevention.

export interface MeshNode {
  id: string;
  name: string;
  rssi: number;
  lastSeen: number;
  isRelay: boolean;
}

export interface SOSMessage {
  id: string;
  senderId: string;
  latitude: number;
  longitude: number;
  status: 'critical' | 'help' | 'safe';
  timestamp: number;
  hops: number;
  path: string[]; // Track the IDs of nodes this message has passed through
}

class BLEMeshService {
  private isScanning: boolean = false;
  private isBroadcasting: boolean = false;
  private connectedNodes: Map<string, MeshNode> = new Map();
  private seenMessages: Set<string> = new Set(); // Prevent message loops (Broadcast Storm prevention)
  private listeners: Set<(message: SOSMessage) => void> = new Set();
  private scanInterval: ReturnType<typeof setInterval> | null = null;
  private cleanupInterval: ReturnType<typeof setInterval> | null = null;
  
  // Simulation parameters
  private readonly MAX_HOPS = 5;
  private readonly NODE_TIMEOUT_MS = 45000; // 45 seconds to consider a node "lost"

  /**
   * Initializes the BLE adapter.
   */
  async initialize(): Promise<boolean> {
    console.log('[BLE Mesh] Initializing SDIRS P2P Mesh Network...');
    // In real implementation, check permissions and adapter state here.
    await new Promise(r => setTimeout(r, 600));
    console.log('[BLE Mesh] Mesh stack ready. Node ID: local-user');
    return true;
  }

  /**
   * Starts scanning for nearby P2P nodes and receiving relayed messages.
   */
  startScanning(onNodesUpdate?: (nodes: MeshNode[]) => void) {
    if (this.isScanning) return;

    this.isScanning = true;
    console.log('[BLE Mesh] Scanning for nearby peers (Module 9 Offline Mode)...');

    // Interval for discovering nodes and receiving data
    this.scanInterval = setInterval(() => {
      this.simulateNodeDiscovery();
      if (onNodesUpdate) onNodesUpdate(Array.from(this.connectedNodes.values()));
      
      // Occasionally receive a message from the mesh
      if (Math.random() > 0.65) {
        this.simulateMeshRelay();
      }
    }, 4000);

    // Interval for cleaning up stale nodes
    this.cleanupInterval = setInterval(() => {
      const now = Date.now();
      let changed = false;
      this.connectedNodes.forEach((node, id) => {
        if (now - node.lastSeen > this.NODE_TIMEOUT_MS) {
          console.log(`[BLE Mesh] Node ${id} timed out.`);
          this.connectedNodes.delete(id);
          changed = true;
        }
      });
      if (changed && onNodesUpdate) {
        onNodesUpdate(Array.from(this.connectedNodes.values()));
      }
    }, 10000);
  }

  /**
   * Broadcasts an SOS message to all nearby peers.
   */
  async broadcastSOS(
    latitude: number,
    longitude: number,
    status: 'critical' | 'help' | 'safe'
  ): Promise<boolean> {
    if (this.isBroadcasting) return false;

    this.isBroadcasting = true;
    const msgId = `msg-${Date.now()}-${Math.random().toString(36).substring(7)}`;
    
    const message: SOSMessage = {
      id: msgId,
      senderId: 'local-user',
      latitude,
      longitude,
      status,
      timestamp: Date.now(),
      hops: 0,
      path: ['local-user']
    };

    this.seenMessages.add(msgId);
    console.log(`[BLE Mesh] INITIATING BROADCAST: ${status} at ${latitude}, ${longitude}`);
    
    // Simulate radio delay
    await new Promise(r => setTimeout(r, 500));
    
    // Log for UI/debug
    console.log(`[BLE Mesh] Message ${msgId} sent to ${this.connectedNodes.size} nearby peers.`);
    
    this.isBroadcasting = false;
    return true;
  }

  /**
   * Relays a message from another node (Flood Routing).
   */
  private async relayMessage(message: SOSMessage) {
    if (this.seenMessages.has(message.id)) return; // Already seen, ignore
    if (message.hops >= this.MAX_HOPS) return; // TTL reached
    if (message.path.includes('local-user')) return; // Loop detected

    this.seenMessages.add(message.id);
    
    const relayedMessage: SOSMessage = {
      ...message,
      hops: message.hops + 1,
      path: [...message.path, 'local-user']
    };

    console.log(`[BLE Mesh] RELAYING message ${message.id} (Hop ${relayedMessage.hops})`);
    
    // Notify local listeners
    this.notifyListeners(relayedMessage);
    
    // In a real system, we'd now re-advertise this packet via BLE.
  }

  private notifyListeners(message: SOSMessage) {
    this.listeners.forEach(cb => {
      try { cb(message); } catch (e) { console.error(e); }
    });
  }

  onSOSReceived(callback: (message: SOSMessage) => void) {
    this.listeners.add(callback);
  }

  offSOSReceived(callback: (message: SOSMessage) => void) {
    this.listeners.delete(callback);
  }

  private simulateNodeDiscovery() {
    // 20% chance to find a new node, otherwise update existing ones
    if (Math.random() > 0.8 && this.connectedNodes.size < 8) {
      const id = `node-${Math.random().toString(36).substring(7)}`;
      this.connectedNodes.set(id, {
        id,
        name: `Citizen_${id.slice(-4)}`,
        rssi: -50,
        lastSeen: Date.now(),
        isRelay: Math.random() > 0.3
      });
      console.log(`[BLE Mesh] New peer discovered: ${id}`);
    } else {
      // Update RSSI of existing nodes to simulate movement
      this.connectedNodes.forEach(node => {
        node.rssi = Math.max(-100, Math.min(-30, node.rssi + (Math.random() * 10 - 5)));
        node.lastSeen = Date.now();
      });
    }
  }

  private simulateMeshRelay() {
    if (this.connectedNodes.size === 0) return;

    const msgId = `msg-relay-${Math.random().toString(16).slice(2, 10)}`;
    const randomNodeId = Array.from(this.connectedNodes.keys())[Math.floor(Math.random() * this.connectedNodes.size)];

    const message: SOSMessage = {
      id: msgId,
      senderId: `orig-user-${Math.random().toString(36).substring(7)}`,
      latitude: 26.84 + (Math.random() * 0.1 - 0.05),
      longitude: 80.94 + (Math.random() * 0.1 - 0.05),
      status: Math.random() > 0.7 ? 'critical' : 'help',
      timestamp: Date.now() - (Math.random() * 60000),
      hops: Math.floor(Math.random() * 3) + 1,
      path: [randomNodeId]
    };

    this.relayMessage(message);
  }

  stopScanning() {
    this.isScanning = false;
    if (this.scanInterval) clearInterval(this.scanInterval);
    if (this.cleanupInterval) clearInterval(this.cleanupInterval);
    this.connectedNodes.clear();
    console.log('[BLE Mesh] Mesh networking paused.');
  }

  getNetworkStatus() {
    return {
      active: this.isScanning,
      peers: this.connectedNodes.size,
      messagesProcessed: this.seenMessages.size
    };
  }
}

export default new BLEMeshService();
