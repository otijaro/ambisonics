import { Hero } from '@/components/home/hero'
import { OptionsSection } from '@/components/home/options-section'
import { VideoPlaceholder } from '@/components/video-placeholder'
import { Reveal } from '@/components/reveal'
import { FeaturesSection } from '@/components/home/features'

export default function HomePage() {
  return (
    <>
      <Hero />
      <section className="py-8 pb-24">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
          <Reveal className="mx-auto max-w-2xl text-center">
            <h2 className="text-balance text-3xl font-semibold tracking-tight sm:text-4xl">
              Conoce el proyecto
            </h2>
            <p className="mt-4 text-pretty text-muted-foreground">
              Una introducción visual a cómo Ambisonic transforma el sonido plano en una experiencia
              espacial completa.
            </p>
          </Reveal>
          <Reveal delay={0.1} className="mt-10 flex justify-center">
            <video 
              src="/intro.mp4" 
              controls 
              playsInline
              className="w-full max-w-4xl rounded-2xl border border-border bg-secondary shadow-lg"
            />
          </Reveal>
        </div>
      </section>

      <FeaturesSection />

      <OptionsSection />
    </>
  )
}
