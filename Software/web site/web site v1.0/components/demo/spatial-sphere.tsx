'use client'

import { motion } from 'framer-motion'
import { User } from 'lucide-react'

interface SpatialSphereProps {
  /** Dirección (azimut) en grados 0–360. 0 = adelante. */
  direccion: number
  /** Altura (elevación) en grados -90 a 90. */
  altura: number
  /** Apertura espacial 0–100. */
  apertura: number
}

const C = 200 // centro
const R = 150 // radio base

export function SpatialSphere({ direccion, altura, apertura }: SpatialSphereProps) {
  // Radio efectivo según apertura (30%–100% del radio).
  const spread = 0.4 + (apertura / 100) * 0.6
  // Elevación reduce el radio horizontal proyectado (cos) y sube/baja en Y.
  const elevRad = (altura * Math.PI) / 180
  const azimRad = (direccion * Math.PI) / 180

  const horizontalR = R * spread * Math.cos(elevRad)
  // En pantalla: adelante (0°) = abajo, siguiendo la referencia (+X adelante hacia abajo).
  const x = C + horizontalR * Math.sin(azimRad)
  const y = C + horizontalR * Math.cos(azimRad) * 0.55 - R * spread * Math.sin(elevRad)

  return (
    <div className="relative mx-auto aspect-square w-full max-w-md">
      <div className="absolute inset-0 rounded-full bg-[radial-gradient(circle,rgba(124,58,237,0.25),transparent_65%)] blur-2xl" />
      <svg viewBox="0 0 400 400" className="relative h-full w-full">
        <defs>
          <linearGradient id="demoRing" x1="0" y1="0" x2="1" y2="1">
            <stop offset="0%" stopColor="#7c3aed" />
            <stop offset="100%" stopColor="#6366f1" />
          </linearGradient>
          <radialGradient id="soundGlow">
            <stop offset="0%" stopColor="#a855f7" />
            <stop offset="100%" stopColor="#6366f1" />
          </radialGradient>
        </defs>

        {/* esfera */}
        <circle cx={C} cy={C} r={R} fill="none" stroke="url(#demoRing)" strokeWidth="1.2" opacity="0.5" />
        {[110, 65].map((rx) => (
          <ellipse key={`v${rx}`} cx={C} cy={C} rx={rx} ry={R} fill="none" stroke="url(#demoRing)" strokeWidth="0.7" opacity="0.28" />
        ))}
        {[R, 100, 55].map((ry) => (
          <ellipse key={`h${ry}`} cx={C} cy={C} rx={R} ry={ry} fill="none" stroke="url(#demoRing)" strokeWidth="0.7" opacity="0.28" />
        ))}

        {/* ejes con etiquetas */}
        <line x1={C} y1={C - R} x2={C} y2={C + R} stroke="url(#demoRing)" strokeWidth="0.6" strokeDasharray="3 5" opacity="0.4" />
        <line x1={C - R} y1={C} x2={C + R} y2={C} stroke="#22c55e" strokeWidth="0.8" opacity="0.5" />
        <text x={C} y={C - R - 8} fill="#a855f7" fontSize="11" textAnchor="middle">arriba</text>
        <text x={C} y={C + R + 18} fill="#a855f7" fontSize="11" textAnchor="middle">abajo</text>
        <text x={C - R - 6} y={C - 8} fill="#22c55e" fontSize="11" textAnchor="end">derecha</text>
        <text x={C + R + 6} y={C - 8} fill="#22c55e" fontSize="11" textAnchor="start">izquierda</text>
        <text x={C + 6} y={C + 40} fill="#22d3ee" fontSize="11" textAnchor="start">adelante</text>

        {/* línea del oyente al sonido */}
        <line x1={C} y1={C} x2={x} y2={y} stroke="url(#demoRing)" strokeWidth="2" opacity="0.8" />

        {/* punto de sonido */}
        <motion.circle
          animate={{ cx: x, cy: y }}
          transition={{ type: 'spring', stiffness: 120, damping: 18 }}
          r="16"
          fill="url(#soundGlow)"
          opacity="0.25"
        />
        <motion.circle
          animate={{ cx: x, cy: y }}
          transition={{ type: 'spring', stiffness: 120, damping: 18 }}
          r="8"
          fill="url(#soundGlow)"
        />
        <motion.circle
          animate={{ cx: x, cy: y }}
          transition={{ type: 'spring', stiffness: 120, damping: 18 }}
          r="3"
          fill="#ffffff"
        />
      </svg>

      {/* oyente */}
      <div className="absolute left-1/2 top-1/2 flex h-14 w-14 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full bg-gradient-to-br from-primary to-violet glow-purple">
        <User className="h-6 w-6 text-primary-foreground" />
      </div>
    </div>
  )
}
