import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle } from 'react-leaflet';
import L from 'leaflet';
import io from 'socket.io-client';
import axios from 'axios';
import { AlertTriangle, Shield, Map as MapIcon, Activity, Users, Radio } from 'lucide-react';
import 'leaflet/dist/leaflet.css';
import './App.css';
import DigitalTwin3D from './components/DigitalTwin3D';

// Fix Leaflet marker icons
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:8000";
const socket = io(API_BASE, {
  transports: ['websocket'],
  reconnection: true,
  reconnectionDelay: 1000,
  reconnectionAttempts: 5
});

function App() {
  const [view, setView] = useState('command'); // 'command' or 'intelligence'
  const [loading, setLoading] = useState(true);
  const [incidents, setIncidents] = useState([]);
  const [heatmapPoints, setHeatmapPoints] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [drones, setDrones] = useState([]);
  const [selectedDrone, setSelectedDrone] = useState(null);
  const [messages, setMessages] = useState([]);
  const [inputText, setInputText] = useState('');
  const [analytics, setAnalytics] = useState(null);
  const [responders, setResponders] = useState({});
  const [stats, setStats] = useState({ total: 0, active: 0, verified: 0, critical: 0 });

  async function fetchIncidents() {
    try {
      const res = await axios.get(`${API_BASE}/api/incidents`);
      setIncidents(res.data);
      
      const criticalCount = res.data.filter(i => i.predicted_severity === 'critical').length;
      const verifiedCount = res.data.filter(i => i.ai_verified).length;
      
      setStats({
        total: res.data.length,
        active: res.data.filter(i => i.status !== 'resolved').length,
        verified: verifiedCount,
        critical: criticalCount
      });
    } catch (err) {
      console.error("Failed to fetch incidents", err);
    }
  }

  async function fetchDrones() {
    try {
      const res = await axios.get(`${API_BASE}/api/drones/fleet`);
      setDrones(res.data.drones);
    } catch (err) {
      console.error("Failed to fetch drones", err);
    }
  }

  async function fetchHeatmap() {
    try {
      const res = await axios.get(`${API_BASE}/api/heatmap`);
      setHeatmapPoints(res.data.points);
    } catch (err) {
      console.error("Failed to fetch heatmap data", err);
    }
  }

  async function fetchAnalytics() {
    try {
      const res = await axios.get(`${API_BASE}/api/dashboard-metrics`);
      setAnalytics(res.data);
    } catch (err) {
      console.error("Failed to fetch analytics", err);
    }
  }

  useEffect(() => {
    const initApp = async () => {
      setLoading(true);
      await Promise.all([
        fetchIncidents(),
        fetchHeatmap(),
        fetchAnalytics(),
        fetchDrones()
      ]);
      setLoading(false);
    };

    initApp();

    const droneInterval = setInterval(fetchDrones, 5000);
    
    // Module 4 & 5: Real-Time Location Updates
    socket.on('location_update', (data) => {
      setResponders(prev => ({ 
        ...prev, 
        [data.id]: {
          ...data,
          lat: data.coords.latitude,
          lon: data.coords.longitude
        } 
      }));
    });

    // Module 9: Emergency Communication
    socket.on('receive_message', (data) => {
      setMessages(prev => [...prev, {
        ...data,
        timestamp: Date.now()
      }]);
    });

    // Module 1 & 4: Emergency Alerts (SOS and New Incidents)
    socket.on('emergency_alert', (data) => {
      console.log("EMERGENCY ALERT:", data);
      // Trigger a visual notification or sound here if needed
      if (data.type.includes('SOS')) {
        // Force refresh incidents or add to a special list
        fetchIncidents();
      }
      
      // Also show in messages as a broadcast
      setMessages(prev => [...prev, {
        sender_name: "SYSTEM ALERT",
        text: `🚨 ${data.message}`,
        type: 'broadcast',
        timestamp: Date.now()
      }]);
    });

    socket.on('incident_update', (data) => {
      fetchIncidents();
    });

    socket.on('prediction_alert', (data) => {
      setPredictions(prev => [data, ...prev.slice(0, 9)]);
    });

    return () => {
      socket.disconnect();
      clearInterval(droneInterval);
    };
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen bg-[#070a0f] text-[#00d4ff]">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-t-2 border-b-2 border-[#00d4ff] mx-auto mb-4"></div>
          <h2 className="text-xl font-bold tracking-widest uppercase">Initializing SDIRS Intelligence...</h2>
          <p className="text-[#4d6a82] mt-2">Connecting to Real-Time Command Network</p>
        </div>
      </div>
    );
  }

  const sendMessage = (e) => {
    e.preventDefault();
    if (!inputText.trim()) return;

    const messageData = {
      sender_id: 0, // 0 for System/Command Center
      sender_name: "COMMAND CENTER",
      text: inputText.trim(),
      type: inputText.startsWith('/') ? 'command' : 'broadcast'
    };

    socket.emit('send_message', messageData);
    setInputText('');
  };

  const getSeverityClass = (sev) => {
    if (sev === 'critical' || sev === 'high') return 'high-severity';
    if (sev === 'medium') return 'medium-severity';
    return 'low-severity';
  };

  const getSeverityBadge = (sev) => {
    const s = sev?.toLowerCase();
    if (s === 'critical' || s === 'high') return 'badge-high';
    if (s === 'medium') return 'badge-medium';
    return 'badge-low';
  };

  const DroneStreamPanel = () => (
    <div className="drone-stream-panel">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 10 }}>
        <h4 style={{ fontSize: '12px', color: 'var(--cy)' }}>
          <Activity size={14} style={{ marginRight: 6, verticalAlign: 'middle' }} />
          LIVE AERIAL INTELLIGENCE: {selectedDrone?.drone_id}
        </h4>
        <button onClick={() => setSelectedDrone(null)} style={{ background: 'none', border: 'none', color: 'var(--tx3)', cursor: 'pointer' }}>✕</button>
      </div>
      <div className="video-placeholder">
        <div className="scan-line"></div>
        <div className="overlay-data">
          <span>ALT: {selectedDrone?.altitude?.toFixed(1)}m</span>
          <span>SPD: {selectedDrone?.speed?.toFixed(1)}km/h</span>
          <span>BAT: {selectedDrone?.battery_percentage}%</span>
        </div>
        <p>RECEIVING ENCRYPTED STREAM...</p>
      </div>
      <div style={{ marginTop: 10, fontSize: '10px', color: 'var(--tx2)', display: 'flex', gap: '15px' }}>
        <span>LAT: {selectedDrone?.lat?.toFixed(5)}</span>
        <span>LON: {selectedDrone?.lon?.toFixed(5)}</span>
        <span style={{ color: 'var(--gn)' }}>STATUS: {selectedDrone?.status?.toUpperCase()}</span>
      </div>
    </div>
  );

  const IntelligenceView = () => (
    <div className="intelligence-view">
      <div className="analytics-grid">
        <div className="analytics-card">
          <h4>SYSTEM PERFORMANCE</h4>
          <div className="metrics-row">
            <div className="metric">
              <span className="label">AVG RESPONSE TIME</span>
              <span className="value">{analytics?.performance?.avg_response_time_minutes ?? '—'}m</span>
            </div>
            <div className="metric">
              <span className="label">RESOLUTION RATE</span>
              <span className="value">92%</span>
            </div>
            <div className="metric">
              <span className="label">AI ACCURACY</span>
              <span className="value">{analytics?.performance?.ai_accuracy_percentage ?? '—'}%</span>
            </div>
          </div>
        </div>

        <div className="analytics-card">
          <h4>RESOURCE UTILIZATION</h4>
          <div className="utilization-list">
            {analytics?.utilization.map((res, idx) => (
              <div key={idx} className="util-item">
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 5 }}>
                  <span style={{ fontSize: '12px' }}>{res.resource_type}</span>
                  <span style={{ fontSize: '11px', color: 'var(--tx3)' }}>{res.active_units}/{res.total_units} Active</span>
                </div>
                <div className="progress-bar">
                  <div style={{ width: `${res.utilization_percentage}%`, background: 'var(--acc)' }}></div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="analytics-card" style={{ marginTop: 20 }}>
        <h4>INCIDENT TRENDS (LAST 7 DAYS)</h4>
        <div className="trends-placeholder">
          {analytics?.trends.slice(0, 14).map((trend, idx) => (
            <div key={idx} className="trend-bar-wrapper">
              <div 
                className={`trend-bar ${trend.severity}`} 
                style={{ height: `${trend.count * 2}px` }}
              ></div>
              <span style={{ fontSize: '8px', marginTop: 5, writingMode: 'vertical-rl' }}>{trend.date.split('-').slice(1).join('/')}</span>
            </div>
          ))}
        </div>
      </div>

      <div className="analytics-card" style={{ marginTop: 20 }}>
        <h4>INCIDENT TYPE DISTRIBUTION</h4>
        <div className="dist-grid">
          {analytics && Object.entries(analytics.incident_types_distribution).map(([type, count]) => (
            <div key={type} className="dist-item">
              <span className="label">{type.toUpperCase()}</span>
              <span className="value">{count}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );

  return (
    <div className="dashboard-container">
      <div className="alert-banner">
        <Radio className="icon-pulse" size={14} style={{ marginRight: 8, display: 'inline' }} />
        LIVE SDIRS COMMAND BROADCAST: Monitoring Active Incident Zones in Lucknow and surrounding areas.
      </div>
      
      <header>
        <div className="logo">
          <Shield size={24} style={{ marginRight: 10, color: 'var(--acc)' }} />
          SDIRS COMMAND CENTER
        </div>
        <div className="view-switcher">
          <button 
            className={view === 'command' ? 'active' : ''} 
            onClick={() => setView('command')}
          >
            COMMAND MAP
          </button>
          <button 
            className={view === 'twin' ? 'active' : ''} 
            onClick={() => setView('twin')}
          >
            DIGITAL TWIN
          </button>
          <button 
            className={view === 'intelligence' ? 'active' : ''} 
            onClick={() => setView('intelligence')}
          >
            AI INTELLIGENCE
          </button>
        </div>
        <div style={{ display: 'flex', gap: '20px', color: 'var(--tx2)', fontSize: '12px' }}>
          <span>SERVER: <span style={{ color: 'var(--gn)' }}>ONLINE</span></span>
          <span>WEBSOCKETS: <span style={{ color: 'var(--gn)' }}>CONNECTED</span></span>
          <span>TIME: {new Date().toLocaleTimeString()}</span>
        </div>
      </header>

      <main className="main-content">
        {/* Sidebar: Incident Feed */}
        <section className="sidebar">
          <h3 style={{ marginBottom: 15, fontSize: '14px', letterSpacing: '1px' }}>
            <Activity size={16} style={{ marginRight: 8, verticalAlign: 'middle' }} />
            REAL-TIME INCIDENTS
          </h3>
          <div className="stats-grid">
            <div className="stat-box">
              <div className="stat-value">{stats.active}</div>
              <div className="stat-label">Active</div>
            </div>
            <div className="stat-box">
              <div className="stat-value">{stats.critical}</div>
              <div className="stat-label">Critical</div>
            </div>
          </div>

          <div className="incident-list">
            {incidents.map(incident => (
              <div key={incident.id} className={`incident-card ${getSeverityClass(incident.predicted_severity)}`}>
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 5 }}>
                  <span style={{ fontSize: '12px', fontWeight: 'bold' }}>{incident.title || incident.incident_type || 'Unknown Incident'}</span>
                  <span className={`severity-badge ${getSeverityBadge(incident.predicted_severity)}`}>
                    {incident.predicted_severity}
                  </span>
                </div>
                <p style={{ fontSize: '11px', color: 'var(--tx2)', marginBottom: 8 }}>{incident.description}</p>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '9px', color: 'var(--tx3)' }}>
                  <span>STATUS: {incident.status.toUpperCase()}</span>
                  <span>{new Date(incident.reported_at).toLocaleTimeString()}</span>
                </div>
                {incident.ai_verified && (
                  <div style={{ marginTop: 5, color: 'var(--cy)', fontSize: '9px', fontWeight: 'bold' }}>
                    <Shield size={10} style={{ marginRight: 4 }} /> AI VERIFIED
                  </div>
                )}
              </div>
            ))}
          </div>

          <div className="communication-panel">
            <h3 style={{ margin: '20px 0 15px', fontSize: '14px', letterSpacing: '1px' }}>
              <Radio size={16} style={{ marginRight: 8, verticalAlign: 'middle' }} />
              COMMUNICATION CHANNEL
            </h3>
            <div className="message-list">
              {messages.length === 0 ? (
                <p style={{ fontSize: '11px', color: 'var(--tx3)', textAlign: 'center', padding: '20px' }}>No active transmissions.</p>
              ) : (
                messages.map((msg, idx) => (
                  <div key={idx} className={`message-item ${msg.type}`}>
                    <span className="sender">{msg.sender_name}:</span>
                    <span className="text">{msg.text}</span>
                  </div>
                ))
              )}
            </div>
            <form onSubmit={sendMessage} className="message-input">
              <input 
                type="text" 
                placeholder="Broadcast to all units..." 
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
              />
            </form>
          </div>
        </section>

        {view === 'twin' ? (
          <section className="map-container">
            <DigitalTwin3D />
          </section>
        ) : view === 'command' ? (
          <>
            {/* Map Center: SDIRS Visual Intelligence */}
            <section className="map-container">
              <MapContainer center={[26.8467, 80.9462]} zoom={13} scrollWheelZoom={true} id="map">
                <TileLayer
                  attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                  url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
                />
                
                {/* Incident Markers */}
                {incidents.map(incident => (
                  <Marker key={incident.id} position={[incident.location.lat, incident.location.lon]}>
                    <Popup>
                      <div style={{ color: '#000' }}>
                        <strong>{incident.incident_type}</strong><br/>
                        {incident.description}<br/>
                        Status: {incident.status}
                      </div>
                    </Popup>
                  </Marker>
                ))}

                {/* Heatmap / Risk Zones */}
                {heatmapPoints.map((point, idx) => (
                  <Circle
                    key={`heatmap-${idx}`}
                    center={[point.lat, point.lon]}
                    radius={point.radius || 500}
                    pathOptions={{
                      color: point.type === 'incident' ? '#ff4d4d' : '#ff944d',
                      fillColor: point.type === 'incident' ? '#ff4d4d' : '#ff944d',
                      fillOpacity: point.intensity * 0.6,
                      stroke: false
                    }}
                  >
                    <Popup>
                      <div style={{ color: '#000' }}>
                        <strong>{point.label}</strong><br/>
                        Intensity: {(point.intensity * 100).toFixed(0)}%<br/>
                        Type: {point.type.toUpperCase()}
                      </div>
                    </Popup>
                  </Circle>
                ))}

                {/* Drone Fleet Markers */}
            {drones.map(drone => (
              <Marker 
                key={drone.drone_id} 
                position={[drone.lat, drone.lon]}
                icon={L.icon({
                  iconUrl: 'https://cdn-icons-png.flaticon.com/512/3063/3063822.png',
                  iconSize: [25, 25],
                })}
              >
                <Popup>
                  <div style={{ color: '#000' }}>
                    <strong>Drone: {drone.drone_id}</strong><br/>
                    Status: {drone.status}<br/>
                    Battery: {drone.battery_percentage}%<br/>
                    <button 
                      onClick={() => setSelectedDrone(drone)}
                      style={{ marginTop: 5, padding: '2px 8px', fontSize: '10px', cursor: 'pointer' }}
                    >
                      VIEW LIVE FEED
                    </button>
                  </div>
                </Popup>
              </Marker>
            ))}

            {/* Responder Markers */}
                {Object.values(responders).map(resp => (
                  <Circle 
                    key={resp.resource_id} 
                    center={[resp.lat, resp.lon]} 
                    radius={200}
                    pathOptions={{ color: 'var(--cy)', fillColor: 'var(--cy)', fillOpacity: 0.5 }}
                  >
                    <Popup>Resource ID: {resp.resource_id}<br/>Status: {resp.status}</Popup>
                  </Circle>
                ))}
              </MapContainer>

              {selectedDrone && <DroneStreamPanel />}
            </section>

            {/* Right Panel: Analytics & Predictions */}
            <section className="right-panel">
              <h3 style={{ marginBottom: 15, fontSize: '14px', letterSpacing: '1px' }}>
                <AlertTriangle size={16} style={{ marginRight: 8, verticalAlign: 'middle' }} />
                AI RISK FORECASTING
              </h3>
              
              <div className="stat-box" style={{ marginBottom: 15 }}>
                <div className="stat-label">AI VERIFICATION ACCURACY</div>
                <div className="stat-value">94.2%</div>
                <div style={{ height: 4, background: 'var(--bd)', borderRadius: 2, marginTop: 8 }}>
                  <div style={{ width: '94%', height: '100%', background: 'var(--pu)' }}></div>
                </div>
              </div>

              <div className="prediction-list">
                <p style={{ fontSize: '10px', color: 'var(--tx3)', marginBottom: 10 }}>ACTIVE PREDICTIONS (MODULE 1)</p>
                {predictions.length === 0 ? (
                  <div style={{ padding: 20, textAlign: 'center', color: 'var(--tx3)', fontSize: '11px' }}>
                    Waiting for AI Prediction Stream...
                  </div>
                ) : (
                  predictions.map((pred, idx) => (
                    <div key={idx} style={{ background: 'var(--bg3)', padding: 10, borderRadius: 6, marginBottom: 8, border: '1px solid var(--bd2)' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 4 }}>
                        <span style={{ fontSize: '11px', color: 'var(--acc3)' }}>{pred.disaster_type} Risk</span>
                        <span style={{ fontSize: '10px', color: 'var(--tx2)' }}>{(pred.probability * 100).toFixed(0)}%</span>
                      </div>
                      <div style={{ height: 3, background: 'var(--bd)', borderRadius: 1.5, marginBottom: 6 }}>
                        <div style={{ width: `${pred.probability * 100}%`, height: '100%', background: 'var(--acc3)' }}></div>
                      </div>
                      <p style={{ fontSize: '9px', color: 'var(--tx3)' }}>LOCATION: {pred.area}</p>
                    </div>
                  ))
                )}
              </div>

              <h3 style={{ marginTop: 30, marginBottom: 15, fontSize: '14px', letterSpacing: '1px' }}>
                <Users size={16} style={{ marginRight: 8, verticalAlign: 'middle' }} />
                RESOURCE STATUS
              </h3>
              <div className="stat-box" style={{ background: 'rgba(0, 212, 255, 0.05)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', marginBottom: 5 }}>
                  <span>Ambulances</span>
                  <span style={{ color: 'var(--gn)' }}>12/15</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px', marginBottom: 5 }}>
                  <span>Fire Units</span>
                  <span style={{ color: 'var(--gn)' }}>8/10</span>
                </div>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '11px' }}>
                  <span>Drones</span>
                  <span style={{ color: 'var(--acc2)' }}>2/4 Active</span>
                </div>
              </div>
            </section>
          </>
        ) : (
          <IntelligenceView />
        )}
      </main>
    </div>
  );
}

export default App;
