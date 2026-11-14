import type { Metadata } from 'next'
import { DemoClient } from '@/components/demo/demo-client'
import { VideoPlaceholder } from '@/components/video-placeholder'
import { Reveal } from '@/components/reveal'

export const metadata: Metadata = {
  title: 'Demo interactiva — Ambisonic',
  description: 'Modifica la posición del sonido en tiempo real y explora el campo sonoro ambisónico.',
}

export default function DemoPage() {
  return (
    <div className="bg-aurora min-h-screen pt-24 pb-16">
      <DemoClient />
    </div>
  )
}
