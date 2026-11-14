import type { Metadata } from 'next'
import { ConversorClient } from '@/components/conversor/conversor-client'

export const metadata: Metadata = {
  title: 'Conversor — Ambisonic',
  description: 'Convierte tu audio estéreo a múltiples formatos espaciales: binaural, cuadrafónico y más.',
}

export default function ConversorPage() {
  return (
    <div className="bg-aurora">
      <section className="mx-auto max-w-7xl px-4 pt-28 pb-24 sm:px-6 sm:pt-32 lg:px-8">
        <div className="max-w-2xl">
          <span className="inline-flex items-center gap-2 rounded-full border border-border bg-secondary/60 px-3 py-1 text-xs text-muted-foreground">
            Opción 1 · Estéreo a ambisónico
          </span>
          <h1 className="mt-5 text-balance text-4xl font-semibold tracking-tight sm:text-5xl">
            Conversor de audio espacial
          </h1>
          <p className="mt-4 text-pretty text-lg leading-relaxed text-muted-foreground">
            Sube una canción estéreo y obtén versiones binaurales y multicanal listas para descargar. Todo el
            procesamiento ocurre automáticamente.
          </p>
        </div>

        <div className="mt-12">
          <ConversorClient />
        </div>
      </section>
    </div>
  )
}
