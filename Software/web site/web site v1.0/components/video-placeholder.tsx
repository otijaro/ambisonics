'use client'

import { motion } from 'framer-motion'
import { Play, Film } from 'lucide-react'
import { cn } from '@/lib/utils'

interface VideoPlaceholderProps {
  title: string
  description?: string
  /** Etiqueta interna para identificar qué video colocar aquí luego. */
  slot?: string
  className?: string
}

/**
 * VideoPlaceholder
 * Espacio reservado para insertar los videos reales del proyecto más adelante,
 * sin modificar el diseño. Reemplaza el contenido interno por un <video> o <iframe>.
 */
export function VideoPlaceholder({ title, description, slot, className }: VideoPlaceholderProps) {
  return (
    <motion.div
      whileHover={{ scale: 1.005 }}
      transition={{ type: 'spring', stiffness: 200, damping: 20 }}
      className={cn(
        'group relative aspect-video w-full overflow-hidden rounded-2xl glass',
        className,
      )}
    >
      {/* Fondo decorativo */}
      <div className="absolute inset-0 bg-[radial-gradient(60%_60%_at_50%_40%,rgba(124,58,237,0.20),transparent_70%)]" />
      <div className="absolute inset-0 opacity-[0.07] [background-image:linear-gradient(rgba(255,255,255,0.5)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.5)_1px,transparent_1px)] [background-size:40px_40px]" />

      <div className="relative flex h-full flex-col items-center justify-center gap-4 p-6 text-center">
        <motion.span
          whileHover={{ scale: 1.08 }}
          className="flex h-16 w-16 items-center justify-center rounded-full bg-primary text-primary-foreground glow-purple"
        >
          <Play className="ml-0.5 h-6 w-6 fill-current" />
        </motion.span>
        <div className="space-y-1">
          <p className="text-balance text-base font-medium text-foreground">{title}</p>
          {description && <p className="text-sm text-muted-foreground">{description}</p>}
        </div>
        <span className="mt-2 inline-flex items-center gap-1.5 rounded-full border border-border bg-background/50 px-3 py-1 text-xs text-muted-foreground">
          <Film className="h-3.5 w-3.5" />
          {slot ? `Espacio de video · ${slot}` : 'Espacio reservado para video'}
        </span>
      </div>
    </motion.div>
  )
}
