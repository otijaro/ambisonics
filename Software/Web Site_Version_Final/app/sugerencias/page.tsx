import type { Metadata } from 'next'
import { FeedbackClient } from '@/components/sugerencias/feedback-client'
import { Reveal } from '@/components/reveal'

export const metadata: Metadata = {
  title: 'Sugerencias · Ambisonic',
  description: 'Envíanos tus ideas, sugerencias o reportes para mejorar Ambisonic.',
}

export default function SugerenciasPage() {
  return (
    <main className="mx-auto min-h-screen max-w-6xl px-4 pb-24 pt-28 sm:px-6">
      <Reveal className="mb-10 text-center">
        <p className="mb-3 text-sm font-medium uppercase tracking-widest text-primary">Sugerencias</p>
        <h1 className="text-balance text-3xl font-bold sm:text-4xl md:text-5xl">
          Tu opinión da forma al sonido
        </h1>
        <p className="mx-auto mt-4 max-w-xl text-pretty text-muted-foreground">
          ¿Tienes una idea, encontraste un error o quieres un nuevo formato de conversión? Escríbenos y lo
          revisaremos.
        </p>
      </Reveal>
      <FeedbackClient />
    </main>
  )
}
