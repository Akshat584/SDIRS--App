// SDIRS Offline Resilience (Module 9)
// Simulates Bluetooth Low Energy (BLE) Mesh Networking for P2P SOS messaging when networks fail.

export interface MeshNode {
  id: string;
  name: string;
  rssi: number;
}

export interface SOSMessage {
  id: string;
  senderId: string;
  latitude: number;
  longitude: number;
  status: 'critical' | 'help' | 'safe';
  timestamp: number;
  hops: number;
}

class BLEMeshService {
  private isScanning: boolean = false;
  private isBroadcasting: boolean = false;
  private connectedNodes: MeshNode[] = [];
  private listeners: ((message: SOSMessage) => void)[] = [];

  /**
   * Initializes the BLE adapter.
   */
  async initialize(): Promise<boolean> {
    console.log("[BLE Mesh] Initializing Bluetooth Low Energy adapter...");
    // Simulating initialization time
    await new Promise(r => setTimeout(r, 500));
    console.log("[BLE Mesh] BLE adapter initialized and ready.");
    return true;
  }

  /**
   * Starts scanning for nearby P2P nodes in the mesh.
   */
  startScanning(onNodeFound?: (nodes: MeshNode[]) => void) {
    if (this.isScanning) return;
    this.isScanning = true;
    console.log("[BLE Mesh] Started scanning for offline mesh nodes.");

    // Simulate finding nearby nodes periodically
    setInterval(() => {
      if (!this.isScanning) return;
      
      const newNodesCount = Math.floor(Math.random() * 3); // 0 to 2 nodes
      const newNodes: MeshNode[] = [];
      for(let i=0; i<newNodesCount; i++) {
        newNodes.push({
          id: `node-${Math.random().toString(36).substring(7)}`,
          name: `Citizen_${Math.floor(Math.random() * 1000)}`,
          rssi: -Math.floor(Math.random() * 50 + 30) // -30 to -80 dBm
        });
      }

      if (newNodes.length > 0) {
        this.connectedNodes = [...this.connectedNodes, ...newNodes];
        if (onNodeFound) onNodeFound(this.connectedNodes);
        
        // Simulate receiving a relayed message occasionally
        if (Math.random() > 0.7) {
          this.simulateIncomingSOS();
        }
      }
    }, 5000);
  }

  stopScanning() {
    this.isScanning = false;
    console.log("[BLE Mesh] Stopped scanning.");
  }

  /**
   * Broadcasts an SOS message via BLE Mesh (Zero-Bandwidth).
   */
  async broadcastSOS(latitude: number, longitude: number, status: 'critical' | 'help' | 'safe'): Promise<boolean> {
    this.isBroadcasting = true;
    console.log(`[BLE Mesh] Broadcasting SOS (${status}) to nearby nodes...`);
    
    const message: SOSMessage = {
      id: `msg-${Date.now()}`,
      senderId: 'local-user',
      latitude,
      longitude,
      status,
      timestamp: Date.now(),
      hops: 0
    };

    // In a real app, this payload is encoded into BLE advertisement packets.
    await new Promise(r => setTimeout(r, 800));
    console.log(`[BLE Mesh] SOS broadcast successful. Reached ${this.connectedNodes.length} nearby nodes.`);
    
    this.isBroadcasting = false;
    return true;
  }

  /**
   * Listens for incoming relayed SOS messages from the mesh.
   */
  onSOSReceived(callback: (message: SOSMessage) => void) {
    this.listeners.push(callback);
  }

  private simulateIncomingSOS() {
    const message: SOSMessage = {
      id: `msg-${Date.now()}`,
      senderId: `node-${Math.random().toString(36).substring(7)}`,
      latitude: 0, // Mock lat
      longitude: 0, // Mock lon
      status: Math.random() > 0.5 ? 'critical' : 'help',
      timestamp: Date.now(),
      hops: Math.floor(Math.random() * 4) + 1 // Relayed 1-4 times
    };

    console.log(`[BLE Mesh] Incoming relayed SOS received! Hops: ${message.hops}`);
    this.listeners.forEach(cb => cb(message));
  }
}

export default new BLEMeshService();
