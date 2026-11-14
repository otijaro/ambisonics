'use client'

import Link from 'next/link'
import { motion } from 'framer-motion'
import { ArrowRight, Headphones, Crosshair, AudioLines } from 'lucide-react'
import { buttonVariants } from '@/components/ui/button'
import { Visualizer3D } from '@/components/demo/visualizer-3d'
import { cn } from '@/lib/utils'

const features = [
  { icon: Headphones, title: 'Inmersión real', desc: 'Sonido que te rodea' },
  { icon: Crosshair, title: 'Control espacial', desc: 'Ajusta dirección y altura' },
  { icon: AudioLines, title: 'Calidad profesional', desc: 'Resultados listos para usar' },
]

export function Hero() {
  return (
    <section className="relative overflow-hidden bg-aurora pt-28 pb-16 sm:pt-32">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <div className="grid items-center gap-12 lg:grid-cols-2">
          <motion.div
            className="lg:-mt-16"
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1] }}
          >
            <span className="inline-flex items-center gap-2 rounded-full border border-border bg-secondary/60 px-3 py-1 text-xs text-muted-foreground">
              <span className="h-1.5 w-1.5 rounded-full bg-primary" />
              Audio espacial · Ambisónico &amp; binaural
            </span>

            <h1 className="mt-5 text-balance text-5xl font-semibold leading-[1.05] tracking-tight sm:text-6xl">
              Convierte tu audio.{' '}
              <span className="bg-gradient-to-r from-primary via-violet to-blue-soft bg-clip-text text-transparent">
                Expande tu mundo.
              </span>
            </h1>

            <p className="mt-6 max-w-xl text-pretty text-lg leading-relaxed text-muted-foreground">
              Transforma audio estéreo en experiencias ambisónicas de alta calidad. Más inmersión, más
              realismo, más emoción.
            </p>

            <div className="mt-8 flex flex-wrap gap-3">
              <Link
                href="/conversor"
                className={cn(buttonVariants({ variant: 'default' }), 'h-12 bg-primary px-6 text-base text-primary-foreground hover:bg-primary/90 glow-purple')}
              >
                Comenzar conversión
                <ArrowRight className="ml-1 h-4 w-4" />
              </Link>
              <Link
                href="/demo"
                className={cn(buttonVariants({ variant: 'outline' }), 'h-12 border-primary/40 bg-transparent px-6 text-base text-foreground hover:bg-accent')}
              >
                Probar demo interactiva
              </Link>
            </div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.9, ease: [0.22, 1, 0.36, 1] }}
          >
            <Visualizer3D mode="autoplay" transparentBg={true} />
          </motion.div>
        </div>

        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, delay: 0.3 }}
          className="mt-14 grid gap-px overflow-hidden rounded-2xl glass sm:grid-cols-3"
        >
          {features.map((f) => (
            <div key={f.title} className="flex items-center gap-4 p-6">
              <span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-xl bg-accent text-primary">
                <f.icon className="h-5 w-5" />
              </span>
              <div>
                <p className="font-medium text-foreground">{f.title}</p>
                <p className="text-sm text-muted-foreground">{f.desc}</p>
              </div>
            </div>
          ))}
        </motion.div>
      </div>
    </section>
  )
}
