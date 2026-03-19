import React, { useEffect, useRef, useState } from 'react';

/**
 * SDIRS Digital Twin / 3D Visualization (Module 9)
 * Uses Three.js for flood and terrain analysis in the command center.
 */
const DigitalTwin3D = () => {
  const mountRef = useRef(null);
  const [floodLevel, setFloodLevel] = useState(0);

  useEffect(() => {
    if (!window.THREE) return;

    const THREE = window.THREE;
    const width = mountRef.current.clientWidth;
    const height = mountRef.current.clientHeight;

    // 1. Scene setup
    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x070a0f);

    // 2. Camera setup
    const camera = new THREE.PerspectiveCamera(75, width / height, 0.1, 1000);
    camera.position.set(20, 20, 20);

    // 3. Renderer setup
    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    mountRef.current.appendChild(renderer.domElement);

    // 4. Orbit Controls (assuming global OrbitControls from CDN)
    let controls;
    if (window.THREE.OrbitControls) {
      controls = new window.THREE.OrbitControls(camera, renderer.domElement);
    }

    // 5. Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
    scene.add(ambientLight);
    const pointLight = new THREE.PointLight(0x00d4ff, 1);
    pointLight.position.set(10, 20, 10);
    scene.add(pointLight);

    // 6. City Grid / Terrain
    const gridHelper = new THREE.GridHelper(50, 50, 0x1a1f26, 0x1a1f26);
    scene.add(gridHelper);

    // 7. City Buildings (Procedural)
    const buildingGeometry = new THREE.BoxGeometry(1, 1, 1);
    for (let i = 0; i < 40; i++) {
        const h = Math.random() * 8 + 1;
        const material = new THREE.MeshPhongMaterial({ 
            color: 0x1a1f26, 
            emissive: 0x00d4ff,
            emissiveIntensity: 0.1,
            specular: 0x00d4ff,
            shininess: 30
        });
        const building = new THREE.Mesh(buildingGeometry, material);
        building.scale.set(1.5, h, 1.5);
        building.position.set(
            (Math.random() - 0.5) * 40,
            h / 2,
            (Math.random() - 0.5) * 40
        );
        scene.add(building);
        
        // Add neon window outlines for "Digital Twin" look
        const edges = new THREE.EdgesGeometry(building.geometry);
        const line = new THREE.LineSegments(edges, new THREE.LineBasicMaterial({ color: 0x00d4ff }));
        line.scale.copy(building.scale);
        line.position.copy(building.position);
        scene.add(line);
    }

    // 8. Flood Plane (Simulation Layer)
    const waterGeometry = new THREE.PlaneGeometry(50, 50);
    const waterMaterial = new THREE.MeshPhongMaterial({ 
        color: 0x00d4ff, 
        transparent: true, 
        opacity: 0.6,
        shininess: 100
    });
    const water = new THREE.Mesh(waterGeometry, waterMaterial);
    water.rotation.x = -Math.PI / 2;
    water.position.y = 0.1; // Start at ground level
    scene.add(water);

    // Animation Loop
    const animate = () => {
      requestAnimationFrame(animate);
      
      // Animate water level based on simulation
      water.position.y = (Math.sin(Date.now() * 0.001) + 1) * 1.5; // Simulate rising/falling
      
      if (controls) controls.update();
      renderer.render(scene, camera);
    };

    animate();

    // Cleanup
    return () => {
      if (mountRef.current) {
        mountRef.current.removeChild(renderer.domElement);
      }
      renderer.dispose();
    };
  }, []);

  return (
    <div style={{ width: '100%', height: '100%', position: 'relative', backgroundColor: '#070a0f', borderRadius: 12, overflow: 'hidden', border: '1px solid rgba(255,255,255,0.05)' }}>
      <div style={{ position: 'absolute', top: 16, left: 16, zIndex: 10, padding: 12, background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(12px)', border: '1px solid rgba(0,212,255,0.3)', borderRadius: 8, pointerEvents: 'none' }}>
        <h3 style={{ color: 'var(--cy)', fontSize: 20, letterSpacing: 2, margin: 0 }}>3D DIGITAL TWIN (BETA)</h3>
        <p style={{ fontSize: 10, color: '#9ca3af', fontFamily: 'monospace', marginTop: 4 }}>MODULE 9: FLOOD & TERRAIN ANALYSIS</p>
        <div style={{ marginTop: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
            <div style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: 'var(--cy)', animation: 'pulse 2s infinite' }} />
            <span style={{ fontSize: 10, color: '#a5f3fc' }}>LIVE TERRAIN SIMULATION</span>
        </div>
      </div>
      
      <div style={{ position: 'absolute', bottom: 16, right: 16, zIndex: 10, display: 'flex', gap: 8 }}>
         <div style={{ padding: 8, background: 'rgba(0,0,0,0.4)', fontSize: 9, color: '#9ca3af', fontFamily: 'monospace', border: '1px solid rgba(255,255,255,0.05)', borderRadius: 4 }}>
            ALT: 250m | POV: ORBIT
         </div>
      </div>

      <div ref={mountRef} style={{ width: '100%', height: '100%' }} />
    </div>
  );
};

export default DigitalTwin3D;
