'use client'

import { motion } from 'framer-motion'
import { Play, Activity, CheckCircle2 } from 'lucide-react'

const features = [
  { 
    icon: Play, 
    title: '¿PARA QUÉ SIRVE?', 
    desc: 'Permite transformar señales estéreo y multicanal en representaciones de audio espacial para análisis, demostración y escucha binaural.' 
  },
  { 
    icon: Activity, 
    title: '¿CÓMO FUNCIONA?', 
    desc: 'El motor DSP procesa la señal, genera las componentes espaciales FOA y realiza el renderizado necesario para obtener diferentes formatos de salida.' 
  },
  { 
    icon: CheckCircle2, 
    title: '¿QUÉ OBTIENES?', 
    desc: 'Archivos de audio procesados para evaluación espacial, incluyendo renderizado binaural y variantes perceptuales preparadas para escucha con audífonos.' 
  },
]

export function FeaturesSection() {
  return (
    <section className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 pb-16">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {features.map((f, i) => (
          <motion.div
            key={f.title}
            initial={{ opacity: 0, y: 24 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ duration: 0.5, delay: i * 0.1 }}
            className="flex flex-col gap-4 p-6 rounded-3xl glass border border-primary/20 shadow-lg hover:shadow-xl hover:-translate-y-1 hover:border-primary/40 transition-all group"
          >
            <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-secondary/80 text-primary group-hover:scale-110 transition-transform shadow-[0_0_15px_rgba(124,58,237,0.15)]">
              <f.icon className="h-6 w-6" />
            </span>
            <div>
              <h3 className="font-bold text-foreground text-sm tracking-widest mb-3">{f.title}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">{f.desc}</p>
            </div>
          </motion.div>
        ))}
      </div>
    </section>
  )
}
