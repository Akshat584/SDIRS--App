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
    <div className="w-full h-full relative bg-[#070a0f] rounded-xl overflow-hidden border border-white/5">
      <div className="absolute top-4 left-4 z-10 p-3 bg-black/60 backdrop-blur-md border border-cyan-500/30 rounded-lg pointer-events-none">
        <h3 className="text-cyan-400 font-bebas text-xl tracking-wider">3D DIGITAL TWIN (BETA)</h3>
        <p className="text-[10px] text-gray-400 font-mono mt-1">MODULE 9: FLOOD & TERRAIN ANALYSIS</p>
        <div className="mt-3 flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-cyan-500 animate-pulse" />
            <span className="text-[10px] text-cyan-200">LIVE TERRAIN SIMULATION</span>
        </div>
      </div>
      
      <div className="absolute bottom-4 right-4 z-10 flex gap-2">
         <div className="p-2 bg-black/40 text-[9px] text-gray-400 font-mono border border-white/5 rounded">
            ALT: 250m | POV: ORBIT
         </div>
      </div>

      <div ref={mountRef} className="w-full h-full" />
    </div>
  );
};

export default DigitalTwin3D;
