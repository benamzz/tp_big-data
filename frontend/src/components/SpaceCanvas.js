import React, { useRef } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Stars } from '@react-three/drei';
import './SpaceCanvas.css';

// Composant pour représenter un objet céleste
function SpaceObject({ position, size, color, isDangerous }) {
  const mesh = useRef();
  
  // Animation de pulsation pour les objets dangereux
  useFrame((state) => {
    if (isDangerous && mesh.current) {
      const pulse = Math.sin(state.clock.elapsedTime * 3) * 0.1 + 1;
      mesh.current.scale.set(pulse, pulse, pulse);
    }
  });

  return (
    <mesh 
      ref={mesh}
      position={[position.x / 100, position.y / 100, position.z / 100]}
    >
      <sphereGeometry args={[size / 5, 32, 32]} />
      <meshStandardMaterial 
        color={color} 
        emissive={isDangerous ? color : 'black'} 
        emissiveIntensity={isDangerous ? 0.5 : 0}
      />
    </mesh>
  );
}

// Composant pour afficher une grille de référence
function Grid() {
  return (
    <gridHelper 
      args={[30, 30, '#444', '#222']}
      position={[0, -10, 0]}
    />
  );
}

// Composant principal de visualisation 3D
const SpaceCanvas = ({ objects, isLoading, error }) => {
  if (isLoading || error) {
    return (
      <div className="space-canvas-container">
        <div className="canvas-message">
          {isLoading ? 'Chargement de la visualisation...' : 'Impossible de charger les données'}
        </div>
      </div>
    );
  }

  return (
    <div className="space-canvas-container">
      <Canvas 
        camera={{ position: [0, 0, 50], fov: 60 }}
        shadows
      >
        <ambientLight intensity={0.3} />
        <pointLight position={[10, 10, 10]} intensity={1} castShadow />
        <Stars radius={100} depth={50} count={5000} factor={4} saturation={0} fade />
        <OrbitControls 
          enablePan={true}
          enableZoom={true}
          enableRotate={true}
          autoRotate={true}
          autoRotateSpeed={0.5}
        />
        <Grid />
        
        {objects.map(obj => {
          const isDangerous = obj.vitesse > 25 && obj.taille > 10;
          return (
            <SpaceObject
              key={obj.id}
              position={obj.position}
              size={obj.taille}
              color={isDangerous ? '#ff5050' : '#4da6ff'}
              isDangerous={isDangerous}
            />
          );
        })}
      </Canvas>
      
      <div className="canvas-legend">
        <div className="legend-item">
          <div className="legend-color" style={{ backgroundColor: '#4da6ff' }}></div>
          <span>Objet standard</span>
        </div>
        <div className="legend-item">
          <div className="legend-color" style={{ backgroundColor: '#ff5050' }}></div>
          <span>Objet dangereux</span>
        </div>
      </div>
    </div>
  );
};

export default SpaceCanvas; 