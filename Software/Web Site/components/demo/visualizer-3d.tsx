'use client'

import React, { useRef, useMemo, useState, useEffect } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { OrbitControls, Text, Sphere } from '@react-three/drei'
import * as THREE from 'three'
import { cn } from '@/lib/utils'
interface Visualizer3DProps {
  mode: 'interactive' | 'autoplay'
  direccion?: number // azimut: -180 to 180 (0 is front, + is right/left depending on convention)
  altura?: number // elevation: -90 to 90
  apertura?: number // spatial width, changes sphere size
  movimiento?: number // movement parameter (not directly affecting visual position unless interactive and driven by state changes)
}

function ResponsiveCamera({ mode }: { mode: 'interactive' | 'autoplay' }) {
  const { camera, size } = useThree()
  useEffect(() => {
    if (camera instanceof THREE.PerspectiveCamera) {
      const isMobile = window.matchMedia('(max-width: 767px)').matches
      
      if (isMobile) {
        // TELÉFONO REAL / viewport < 768 px
        camera.fov = 65
        camera.position.set(7, 5, 8)
        camera.zoom = 1.25
      } else {
        // ESCRITORIO / viewport >= 768 px
        if (mode === 'interactive') {
          // Demo interactive desktop
          camera.fov = 45
          camera.position.set(5, 4, 6)
          camera.zoom = 1.03
        } else {
          // Inicio autoplay desktop
          camera.fov = 45
          camera.position.set(5, 4, 6)
          camera.zoom = 1
        }
      }
      camera.updateProjectionMatrix()
    }
  }, [size.width, size.height, camera, mode])
  return null
}

function Scene({ mode, direccion = 0, altura = 20, apertura = 50, movimiento = 0 }: Visualizer3DProps) {
  const sphereRef = useRef<THREE.Mesh>(null)
  const targetPos = useMemo(() => new THREE.Vector3(), [])
  
  useFrame((state) => {
    if (!sphereRef.current) return
    
    if (mode === 'autoplay') {
      const t = state.clock.getElapsedTime()
      const speed = 0.8
      const radius = 3
      // Movimiento 3D en bucle pasando por frente, izquierda, atrás, derecha, arriba, abajo
      const x = Math.sin(t * speed) * radius
      const z = -Math.cos(t * speed) * radius
      const y = Math.sin(t * speed * 1.5) * 2 // Varía en altura
      
      sphereRef.current.position.set(x, y, z)
    } else if (mode === 'interactive') {
      const movAmount = movimiento / 100
      const animSpeed = movAmount * 2
      const timeOffset = state.clock.getElapsedTime() * animSpeed
      
      const baseAzim = (-direccion * Math.PI) / 180
      const azimRad = baseAzim + timeOffset // Movimiento orbital continuo horizontal
      
      const baseElev = (altura * Math.PI) / 180
      // Oscilación vertical leve si hay movimiento
      const elevRad = baseElev + (movAmount > 0 ? Math.sin(state.clock.getElapsedTime() * animSpeed * 1.5) * 0.5 * movAmount : 0)
      
      // La apertura podría cambiar el tamaño de la esfera
      const scale = 0.5 + (apertura / 100) * 1.5
      sphereRef.current.scale.set(scale, scale, scale)
      
      const distance = 3
      
      targetPos.set(
        Math.sin(azimRad) * Math.cos(elevRad) * distance,
        Math.sin(elevRad) * distance,
        -Math.cos(azimRad) * Math.cos(elevRad) * distance
      )
      
      // Interpolación suave para movimiento fluido cuando el usuario cambia los sliders
      sphereRef.current.position.lerp(targetPos, 0.1)
    }
  })

  return (
    <>
      <ambientLight intensity={0.6} />
      <directionalLight position={[5, 10, 5]} intensity={1.5} />
      <pointLight position={[0, 0, 0]} intensity={0.5} color="#7c3aed" />
      
      {/* Oyente (Centro) - Representación estilizada cabeza y hombros */}
      <group position={[0, -0.2, 0]}>
        {/* Cabeza */}
        <Sphere args={[0.2, 16, 16]} position={[0, 0.45, 0]}>
          <meshStandardMaterial color="#22c55e" roughness={0.4} emissive="#22c55e" emissiveIntensity={0.2} />
        </Sphere>
        {/* Hombros / Torso (esfera achatada) */}
        <Sphere args={[0.35, 16, 16]} position={[0, 0, 0]} scale={[1, 0.6, 0.5]}>
          <meshStandardMaterial color="#22c55e" roughness={0.4} emissive="#22c55e" emissiveIntensity={0.1} />
        </Sphere>
      </group>

      {/* Fuente de Audio (Esfera) */}
      <Sphere ref={sphereRef} args={[0.2, 16, 16]} position={[0, 0, -3]}>
        <meshStandardMaterial color="#a855f7" emissive="#a855f7" emissiveIntensity={0.6} roughness={0.3} />
      </Sphere>
      
      {/* Línea o Vector de conexión */}
      <LinePoints sphereRef={sphereRef} />

      {/* Anillos de referencia plana (horizontal y vertical) */}
      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <ringGeometry args={[2.98, 3.02, 64]} />
        <meshBasicMaterial color="#4f46e5" transparent opacity={0.2} side={THREE.DoubleSide} />
      </mesh>
      
      {/* Ejes visuales */}
      <gridHelper args={[8, 8, '#4f46e5', '#3730a3']} position={[0, -3.5, 0]} material-opacity={0.15} material-transparent />
      
      {/* Etiquetas */}
      <Text position={[0, 0, -3.5]} fontSize={0.25} color="#22d3ee" anchorY="bottom">FRENTE</Text>
      <Text position={[0, 0, 3.5]} fontSize={0.25} color="#a855f7" anchorY="bottom" rotation={[0, Math.PI, 0]}>ATRÁS</Text>
      <Text position={[-3.5, 0, 0]} fontSize={0.25} color="#22c55e" anchorY="bottom" rotation={[0, Math.PI / 2, 0]}>IZQ</Text>
      <Text position={[3.5, 0, 0]} fontSize={0.25} color="#22c55e" anchorY="bottom" rotation={[0, -Math.PI / 2, 0]}>DER</Text>
      
      <Text position={[0, 2.75, 0]} fontSize={0.25} color="#f43f5e" anchorY="bottom">ARRIBA</Text>
      <Text position={[0, -3.5, 0]} fontSize={0.25} color="#f43f5e" anchorY="bottom">ABAJO</Text>

      <OrbitControls 
        enableZoom={false} 
        enablePan={false} 
        autoRotate={mode === 'autoplay'} 
        autoRotateSpeed={1}
        maxPolarAngle={Math.PI / 1.5}
        minPolarAngle={Math.PI / 4}
      />
    </>
  )
}

function LinePoints({ sphereRef }: { sphereRef: React.RefObject<THREE.Mesh> }) {
  const lineRef = useRef<THREE.Line>(null)
  const geometry = useMemo(() => new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0,0,0), new THREE.Vector3(0,0,-3)]), [])
  
  useFrame(() => {
    if (lineRef.current && sphereRef.current) {
      const positions = lineRef.current.geometry.attributes.position.array as Float32Array
      positions[3] = sphereRef.current.position.x
      positions[4] = sphereRef.current.position.y
      positions[5] = sphereRef.current.position.z
      lineRef.current.geometry.attributes.position.needsUpdate = true
    }
  })
  
  return (
    <line ref={lineRef} geometry={geometry}>
      <lineBasicMaterial color="#a855f7" linewidth={3} transparent opacity={0.6} />
    </line>
  )
}

export function Visualizer3D(props: Visualizer3DProps & { transparentBg?: boolean }) {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    let frameId: number
    frameId = requestAnimationFrame(() => {
      setMounted(true)
    })
    return () => cancelAnimationFrame(frameId)
  }, [])

  return (
    <div className={cn(
      "w-full h-[360px] md:h-[440px] max-w-full relative overflow-hidden",
      props.transparentBg 
        ? "bg-transparent" 
        : "rounded-2xl border border-border bg-gradient-to-b from-secondary/50 to-background"
    )}>
      {mounted && (
        <Canvas 
          camera={{ position: [5, 4, 6], fov: 45 }}
          dpr={[1, 1.5]}
          gl={{ antialias: true, powerPreference: 'high-performance' }}
        >
          <ResponsiveCamera mode={props.mode} />
          <Scene {...props} />
        </Canvas>
      )}
      {props.mode === 'interactive' && (
        <div className="absolute bottom-3 right-3 text-[10px] text-muted-foreground uppercase tracking-widest bg-background/50 px-2 py-1 rounded backdrop-blur-md">
          Arrastra para orbitar
        </div>
      )}
    </div>
  )
}
