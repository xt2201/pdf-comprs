import { useRef, useMemo } from 'react'
import { Canvas, useFrame } from '@react-three/fiber'
import { Points, PointMaterial } from '@react-three/drei'
import * as THREE from 'three'

function ParticleField() {
  const ref = useRef<THREE.Points>(null)
  
  const count = 800
  
  const positions = useMemo(() => {
    const positions = new Float32Array(count * 3)
    for (let i = 0; i < count; i++) {
      const i3 = i * 3
      positions[i3] = (Math.random() - 0.5) * 20
      positions[i3 + 1] = (Math.random() - 0.5) * 20
      positions[i3 + 2] = (Math.random() - 0.5) * 20
    }
    return positions
  }, [])
  
  useFrame((state) => {
    if (ref.current) {
      ref.current.rotation.x = state.clock.elapsedTime * 0.02
      ref.current.rotation.y = state.clock.elapsedTime * 0.03
    }
  })
  
  return (
    <Points ref={ref} positions={positions} stride={3} frustumCulled={false}>
      <PointMaterial
        transparent
        color="#667eea"
        size={0.02}
        sizeAttenuation={true}
        depthWrite={false}
        opacity={0.6}
      />
    </Points>
  )
}

function FloatingShapes() {
  const groupRef = useRef<THREE.Group>(null)
  
  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.y = state.clock.elapsedTime * 0.05
      groupRef.current.position.y = Math.sin(state.clock.elapsedTime * 0.3) * 0.5
    }
  })
  
  return (
    <group ref={groupRef}>
      {/* Floating geometric shapes */}
      <mesh position={[-3, 2, -5]}>
        <icosahedronGeometry args={[0.5, 0]} />
        <meshStandardMaterial
          color="#764ba2"
          transparent
          opacity={0.3}
          wireframe
        />
      </mesh>
      
      <mesh position={[4, -1, -4]}>
        <octahedronGeometry args={[0.7, 0]} />
        <meshStandardMaterial
          color="#667eea"
          transparent
          opacity={0.3}
          wireframe
        />
      </mesh>
      
      <mesh position={[-2, -2, -6]}>
        <tetrahedronGeometry args={[0.6, 0]} />
        <meshStandardMaterial
          color="#764ba2"
          transparent
          opacity={0.2}
          wireframe
        />
      </mesh>
      
      <mesh position={[3, 3, -7]}>
        <dodecahedronGeometry args={[0.4, 0]} />
        <meshStandardMaterial
          color="#667eea"
          transparent
          opacity={0.25}
          wireframe
        />
      </mesh>
    </group>
  )
}

export function Background3D() {
  return (
    <div className="three-canvas">
      <Canvas
        camera={{ position: [0, 0, 5], fov: 60 }}
        dpr={[1, 2]}
        style={{ background: 'transparent' }}
      >
        <ambientLight intensity={0.5} />
        <directionalLight position={[10, 10, 5]} intensity={0.5} />
        <ParticleField />
        <FloatingShapes />
      </Canvas>
    </div>
  )
}
