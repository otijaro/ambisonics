'use client'

import React, { useRef, useMemo, useState, useEffect } from 'react'
import { Canvas, useFrame, useThree } from '@react-three/fiber'
import { OrbitControls, Text, Sphere, Billboard } from '@react-three/drei'
import * as THREE from 'three'
import { cn } from '@/lib/utils'

interface Visualizer3DProps {
  mode: 'interactive' | 'autoplay'
  direccion?: number // azimut: -180 to 180 (0 is front, + is right/left depending on convention)
  altura?: number // elevation: -90 to 90
  apertura?: number // spatial width, changes sphere size
  movimiento?: number // movement parameter
}

function ResponsiveCamera({ mode }: { mode: 'interactive' | 'autoplay' }) {
  const { camera, size } = useThree()
  useEffect(() => {
    if (camera instanceof THREE.PerspectiveCamera) {
      const isMobile = window.matchMedia('(max-width: 767px)').matches
      
      if (isMobile) {
        camera.fov = 65
        camera.position.set(6, 3.5, 7)
        camera.zoom = 1.15
      } else {
        camera.fov = 45
        camera.position.set(4.8, 3.2, 5.8)
        camera.zoom = 1.05
      }
      camera.updateProjectionMatrix()
    }
  }, [size.width, size.height, camera, mode])
  return null
}

function Scene({ mode, direccion = 0, altura = 0, apertura = 0, movimiento = 0 }: Visualizer3DProps) {
  const sphereRef = useRef<THREE.Mesh>(null)
  const shadowRef = useRef<THREE.Mesh>(null)
  const targetPos = useMemo(() => new THREE.Vector3(), [])
  
  useFrame((state) => {
    if (!sphereRef.current) return
    
    if (mode === 'autoplay') {
      const t = state.clock.getElapsedTime()
      const speed = 0.8
      const radius = 3
      const x = Math.sin(t * speed) * radius
      const z = -Math.cos(t * speed) * radius
      const y = Math.sin(t * speed * 1.5) * 2
      
      sphereRef.current.position.set(x, y, z)
      if (shadowRef.current) {
        shadowRef.current.position.set(x, 0, z)
      }
    } else if (mode === 'interactive') {
      const movAmount = movimiento / 100
      const animSpeed = movAmount * 2
      const timeOffset = state.clock.getElapsedTime() * animSpeed
      
      const baseAzim = (-direccion * Math.PI) / 180
      const azimRad = baseAzim + timeOffset
      
      const baseElev = (altura * Math.PI) / 180
      const elevRad = baseElev + (movAmount > 0 ? Math.sin(state.clock.getElapsedTime() * animSpeed * 1.5) * 0.4 * movAmount : 0)
      
      const scale = 0.45 + (apertura / 100) * 1.3
      sphereRef.current.scale.set(scale, scale, scale)
      
      const distance = 3
      
      targetPos.set(
        Math.sin(azimRad) * Math.cos(elevRad) * distance,
        Math.sin(elevRad) * distance,
        -Math.cos(azimRad) * Math.cos(elevRad) * distance
      )
      
      sphereRef.current.position.lerp(targetPos, 0.15)

      // Actualizar posición de la proyección sobre el plano horizontal Y = 0
      if (shadowRef.current) {
        shadowRef.current.position.set(
          sphereRef.current.position.x,
          0,
          sphereRef.current.position.z
        )
      }
    }
  })

  return (
    <>
      <ambientLight intensity={0.7} />
      <directionalLight position={[5, 10, 5]} intensity={1.5} />
      <pointLight position={[0, 0, 0]} intensity={0.6} color="#7c3aed" />
      
      {/* Oyente (Centro) - Representación cabeza y torso orientada al frente */}
      <group position={[0, -0.2, 0]}>
        {/* Cabeza */}
        <Sphere args={[0.22, 16, 16]} position={[0, 0.45, 0]}>
          <meshStandardMaterial color="#22c55e" roughness={0.35} emissive="#22c55e" emissiveIntensity={0.25} />
        </Sphere>
        {/* Nariz (indicador visual de orientación frontal) */}
        <Sphere args={[0.06, 12, 12]} position={[0, 0.45, -0.24]} scale={[1, 1, 1.4]}>
          <meshStandardMaterial color="#16a34a" roughness={0.4} />
        </Sphere>
        {/* Hombros / Torso */}
        <Sphere args={[0.38, 16, 16]} position={[0, 0, 0]} scale={[1, 0.65, 0.5]}>
          <meshStandardMaterial color="#22c55e" roughness={0.4} emissive="#22c55e" emissiveIntensity={0.15} />
        </Sphere>
      </group>

      {/* Fuente de Audio (Esfera morada) */}
      <Sphere ref={sphereRef} args={[0.22, 16, 16]} position={[0, 0, -3]}>
        <meshStandardMaterial color="#a855f7" emissive="#a855f7" emissiveIntensity={0.7} roughness={0.25} />
      </Sphere>

      {/* Sombra / Proyección horizontal sobre el plano Y = 0 */}
      <mesh ref={shadowRef} position={[0, 0, -3]} rotation={[-Math.PI / 2, 0, 0]}>
        <circleGeometry args={[0.18, 24]} />
        <meshBasicMaterial color="#a855f7" transparent opacity={0.35} side={THREE.DoubleSide} />
      </mesh>
      
      {/* Líneas de conexión 3D: vector al centro + tallo vertical de altura */}
      <ConnectorLines sphereRef={sphereRef} />

      {/* Anillo de referencia horizontal (Plano Y = 0) */}
      <mesh rotation={[Math.PI / 2, 0, 0]}>
        <ringGeometry args={[2.97, 3.03, 64]} />
        <meshBasicMaterial color="#4f46e5" transparent opacity={0.35} side={THREE.DoubleSide} />
      </mesh>

      {/* Anillo vertical sagital de referencia (Frente - Cenit - Atrás - Nadir) */}
      <mesh rotation={[0, Math.PI / 2, 0]}>
        <ringGeometry args={[2.98, 3.02, 64]} />
        <meshBasicMaterial color="#3b82f6" transparent opacity={0.15} side={THREE.DoubleSide} />
      </mesh>

      {/* Anillo vertical lateral de referencia (Izquierda - Cenit - Derecha - Nadir) */}
      <mesh rotation={[0, 0, 0]}>
        <ringGeometry args={[2.98, 3.02, 64]} />
        <meshBasicMaterial color="#10b981" transparent opacity={0.15} side={THREE.DoubleSide} />
      </mesh>
      
      {/* Ejes visuales inferiores */}
      <gridHelper args={[7, 7, '#4f46e5', '#3730a3']} position={[0, -3.2, 0]} material-opacity={0.12} material-transparent />
      
      {/* Etiquetas Espaciales con auto-orientación hacia la cámara (Billboard) */}
      <Billboard position={[0, 0, -3.4]}>
        <Text fontSize={0.24} color="#22d3ee" anchorY="bottom" outlineWidth={0.02} outlineColor="#000">
          FRENTE
        </Text>
      </Billboard>

      <Billboard position={[0, 0, 3.4]}>
        <Text fontSize={0.24} color="#a855f7" anchorY="bottom" outlineWidth={0.02} outlineColor="#000">
          ATRÁS
        </Text>
      </Billboard>

      <Billboard position={[-3.4, 0, 0]}>
        <Text fontSize={0.24} color="#22c55e" anchorY="bottom" outlineWidth={0.02} outlineColor="#000">
          IZQ
        </Text>
      </Billboard>

      <Billboard position={[3.4, 0, 0]}>
        <Text fontSize={0.24} color="#22c55e" anchorY="bottom" outlineWidth={0.02} outlineColor="#000">
          DER
        </Text>
      </Billboard>
      
      <Billboard position={[0, 3.25, 0]}>
        <Text fontSize={0.24} color="#f43f5e" anchorY="bottom" outlineWidth={0.02} outlineColor="#000">
          CENIT (+90°)
        </Text>
      </Billboard>

      <Billboard position={[0, -3.25, 0]}>
        <Text fontSize={0.24} color="#f43f5e" anchorY="top" outlineWidth={0.02} outlineColor="#000">
          NADIR (-90°)
        </Text>
      </Billboard>

      {/* Controles de cámara con rango polar amplio para ver arriba y abajo con claridad */}
      <OrbitControls 
        enableZoom={true} 
        enablePan={false} 
        autoRotate={mode === 'autoplay'} 
        autoRotateSpeed={0.8}
        maxPolarAngle={Math.PI * 0.92} // Permite orbitar hasta casi el polo sur para ver elevaciones negativas
        minPolarAngle={Math.PI * 0.08} // Permite orbitar hasta casi el polo norte
      />
    </>
  )
}

function ConnectorLines({ sphereRef }: { sphereRef: React.RefObject<THREE.Mesh> }) {
  const lineCenterRef = useRef<THREE.Line>(null)
  const lineStemRef = useRef<THREE.Line>(null)

  const geomCenter = useMemo(() => new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0,0,0), new THREE.Vector3(0,0,-3)]), [])
  const geomStem = useMemo(() => new THREE.BufferGeometry().setFromPoints([new THREE.Vector3(0,0,-3), new THREE.Vector3(0,0,-3)]), [])
  
  useFrame(() => {
    if (sphereRef.current) {
      const sx = sphereRef.current.position.x
      const sy = sphereRef.current.position.y
      const sz = sphereRef.current.position.z

      // Línea 1: Vector radial desde el centro hacia la esfera
      if (lineCenterRef.current) {
        const pos = lineCenterRef.current.geometry.attributes.position.array as Float32Array
        pos[0] = 0; pos[1] = 0; pos[2] = 0
        pos[3] = sx; pos[4] = sy; pos[5] = sz
        lineCenterRef.current.geometry.attributes.position.needsUpdate = true
      }

      // Línea 2: Tallo vertical desde la sombra (plano Y=0) hasta la esfera en altura
      if (lineStemRef.current) {
        const posStem = lineStemRef.current.geometry.attributes.position.array as Float32Array
        posStem[0] = sx; posStem[1] = 0; posStem[2] = sz
        posStem[3] = sx; posStem[4] = sy; posStem[5] = sz
        lineStemRef.current.geometry.attributes.position.needsUpdate = true
      }
    }
  })
  
  return (
    <>
      {/* Vector radial morado */}
      <line ref={lineCenterRef} geometry={geomCenter}>
        <lineBasicMaterial color="#a855f7" linewidth={2.5} transparent opacity={0.65} />
      </line>

      {/* Tallo vertical cian que hace visible la altura exacta por encima/debajo del plano */}
      <line ref={lineStemRef} geometry={geomStem}>
        <lineDashedMaterial color="#22d3ee" linewidth={1.5} dashSize={0.15} gapSize={0.08} transparent opacity={0.8} />
      </line>
    </>
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
          camera={{ position: [4.8, 3.2, 5.8], fov: 45 }}
          dpr={[1, 1.5]}
          gl={{ antialias: true, powerPreference: 'high-performance' }}
        >
          <ResponsiveCamera mode={props.mode} />
          <Scene {...props} />
        </Canvas>
      )}
      {props.mode === 'interactive' && (
        <div className="absolute bottom-3 right-3 text-[10px] text-muted-foreground uppercase tracking-widest bg-background/50 px-2 py-1 rounded backdrop-blur-md">
          Arrastra para orbitar 360°
        </div>
      )}
    </div>
  )
}
