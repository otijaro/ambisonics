'use client'

import Image from 'next/image'
import Link from 'next/link'
import { ArrowRight, Check } from 'lucide-react'
import { buttonVariants } from '@/components/ui/button'
import { Reveal } from '@/components/reveal'
import { cn } from '@/lib/utils'

const cards = [
  {
    tag: 'Opción 1',
    image: '/opcion-1.png',
    imageAlt: 'Infografía: de audio estéreo a formato ambisónico',
    title: 'Conversión de estéreo a ambisónico',
    desc: 'Convierte cualquier canción estéreo en una experiencia sonora envolvente, sin cambiar tu música: solo más espacio para sentirla.',
    points: ['Procesamiento ambisónico', 'Salida binaural', 'Audio espacial 360°'],
    cta: { label: 'Ir al conversor', href: '/conversor' },
  },
  {
    tag: 'Opción 2',
    image: '/opcion-2.png',
    imageAlt: 'Infografía: configuración tetraédrica de 4 micrófonos',
    title: 'Configuración tetraédrica de 4 micrófonos',
    desc: 'Captura una escena sonora con 4 canales simultáneos (FLU, FRD, BLD, BRU) y conviértela a formato ambisónico para una escucha espacial realista.',
    points: ['4 micrófonos orientados', '4 canales simultáneos', 'Codificación W · X · Y · Z'],
    cta: { label: 'Ir al conversor', href: '/conversor' },
  },
]

export function OptionsSection() {
  return (
    <section className="relative py-20 sm:py-24">
      <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
        <Reveal className="mx-auto max-w-2xl text-center">
          <h2 className="text-balance text-3xl font-semibold tracking-tight sm:text-4xl">
            ¿Qué puede hacer la plataforma?
          </h2>
          <p className="mt-4 text-pretty text-muted-foreground">
            Dos caminos para llevar tu audio al espacio: convierte una pista estéreo existente o captura una
            escena completa con una configuración tetraédrica.
          </p>
        </Reveal>

        <div className="mt-14 grid gap-8 lg:grid-cols-2">
          {cards.map((card, i) => (
            <Reveal key={card.tag} delay={i * 0.1}>
              <article className="flex h-full flex-col overflow-hidden rounded-3xl glass">
                <div className="relative aspect-[16/9] w-full overflow-hidden border-b border-border bg-secondary">
                  <Image
                    src={card.image || '/placeholder.svg'}
                    alt={card.imageAlt}
                    fill
                    className="object-cover"
                    sizes="(max-width: 1024px) 100vw, 50vw"
                  />
                </div>
                <div className="flex flex-1 flex-col p-6 sm:p-8">
                  <span className="w-fit rounded-full bg-primary/15 px-3 py-1 text-xs font-medium text-primary">
                    {card.tag}
                  </span>
                  <h3 className="mt-4 text-xl font-semibold text-foreground">{card.title}</h3>
                  <p className="mt-3 text-sm leading-relaxed text-muted-foreground">{card.desc}</p>

                  <ul className="mt-5 space-y-2.5">
                    {card.points.map((p) => (
                      <li key={p} className="flex items-center gap-2.5 text-sm text-foreground">
                        <span className="flex h-5 w-5 items-center justify-center rounded-full bg-accent text-primary">
                          <Check className="h-3 w-3" />
                        </span>
                        {p}
                      </li>
                    ))}
                  </ul>

                  <Link
                    href={card.cta.href}
                    className={cn(
                      buttonVariants({ variant: 'default' }),
                      'mt-7 h-11 w-fit bg-primary px-5 text-primary-foreground hover:bg-primary/90',
                    )}
                  >
                    {card.cta.label}
                    <ArrowRight className="ml-1 h-4 w-4" />
                  </Link>
                </div>
              </article>
            </Reveal>
          ))}
        </div>
      </div>
    </section>
  )
}
