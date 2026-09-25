'use client'

import { motion } from 'framer-motion'
import { User } from 'lucide-react'
import { cn } from '@/lib/utils'

/** Esfera ambisónica luminosa (solo SVG + CSS) para el hero. */
export function HeroSphere({ className }: { className?: string }) {
  const dots = [
    { cx: 200, cy: 40, color: 'var(--violet)' },
    { cx: 360, cy: 200, color: 'var(--primary)' },
    { cx: 200, cy: 360, color: 'var(--blue-soft)' },
    { cx: 40, cy: 200, color: 'var(--primary)' },
    { cx: 300, cy: 110, color: 'var(--blue-soft)' },
    { cx: 300, cy: 300, color: 'var(--violet)' },
  ]

  return (
    <div className={cn('relative mx-auto aspect-square w-full max-w-lg', className)}>
      {/* halo */}
      <div className="absolute inset-0 rounded-full bg-[radial-gradient(circle,rgba(124,58,237,0.35),transparent_60%)] blur-2xl" />

      <motion.div
        animate={{ y: [0, -12, 0] }}
        transition={{ duration: 7, repeat: Infinity, ease: 'easeInOut' }}
        className="relative h-full w-full"
      >
        <svg viewBox="0 0 400 400" className="h-full w-full">
          <defs>
            <radialGradient id="sphereFill" cx="42%" cy="38%" r="65%">
              <stop offset="0%" stopColor="rgba(124,58,237,0.35)" />
              <stop offset="60%" stopColor="rgba(76,29,149,0.12)" />
              <stop offset="100%" stopColor="rgba(9,9,11,0)" />
            </radialGradient>
            <linearGradient id="ring" x1="0" y1="0" x2="1" y2="1">
              <stop offset="0%" stopColor="#7c3aed" />
              <stop offset="100%" stopColor="#6366f1" />
            </linearGradient>
          </defs>

          <circle cx="200" cy="200" r="160" fill="url(#sphereFill)" />
          <circle cx="200" cy="200" r="160" fill="none" stroke="url(#ring)" strokeWidth="1" opacity="0.5" />

          {/* meridianos / paralelos giratorios */}
          <g className="animate-spin-slow" style={{ transformOrigin: '200px 200px' }}>
            {[160, 120, 70].map((rx) => (
              <ellipse key={`v${rx}`} cx="200" cy="200" rx={rx} ry="160" fill="none" stroke="url(#ring)" strokeWidth="0.8" opacity="0.3" />
            ))}
            {[160, 120, 70].map((ry) => (
              <ellipse key={`h${ry}`} cx="200" cy="200" rx="160" ry={ry} fill="none" stroke="url(#ring)" strokeWidth="0.8" opacity="0.3" />
            ))}
          </g>

          {/* ejes */}
          <line x1="200" y1="20" x2="200" y2="380" stroke="url(#ring)" strokeWidth="0.6" strokeDasharray="3 5" opacity="0.4" />
          <line x1="20" y1="200" x2="380" y2="200" stroke="url(#ring)" strokeWidth="0.6" strokeDasharray="3 5" opacity="0.4" />

          {/* puntos de sonido */}
          {dots.map((d, i) => (
            <g key={i}>
              <circle cx={d.cx} cy={d.cy} r="9" fill={d.color} opacity="0.25">
                <animate attributeName="r" values="9;14;9" dur="3s" begin={`${i * 0.4}s`} repeatCount="indefinite" />
              </circle>
              <circle cx={d.cx} cy={d.cy} r="5" fill={d.color} />
            </g>
          ))}
        </svg>

        {/* Oyente al centro */}
        <div className="absolute left-1/2 top-1/2 flex h-16 w-16 -translate-x-1/2 -translate-y-1/2 items-center justify-center rounded-full bg-gradient-to-br from-primary to-violet glow-purple">
          <User className="h-7 w-7 text-primary-foreground" />
        </div>
      </motion.div>
    </div>
  )
}
