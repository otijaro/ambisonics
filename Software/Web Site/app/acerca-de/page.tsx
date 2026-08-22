import React from 'react'
import type { Metadata } from 'next'
import { GraduationCap, Users, UserCog, Building2, Lightbulb, Cog, Rocket, FlaskConical, CheckCircle2 } from 'lucide-react'
import { Reveal } from '@/components/reveal'

export const metadata: Metadata = {
  title: 'Acerca de — Ambisonic',
  description: 'Conoce el proyecto Ambisonic, su trayectoria y el equipo detrás de la Universidad Industrial de Santander.',
}

const timeline = [
  { icon: Lightbulb, title: 'CONCEPCIÓN DEL SISTEMA', text: 'Definición de la arquitectura para procesar señales estéreo y multicanal mediante Ambisonics de primer orden.' },
  { icon: FlaskConical, title: 'INVESTIGACIÓN DSP', text: 'Estudio de codificación FOA, STFT, coordenadas espaciales, convolución binaural y modelos HRTF.' },
  { icon: Cog, title: 'MOTOR DE PROCESAMIENTO', text: 'Desarrollo en Python del núcleo DSP para conversión estéreo–FOA, arreglos tetraédricos y renderizado binaural.' },
  { icon: Rocket, title: 'PLATAFORMA WEB', text: 'Integración del motor DSP con FastAPI y Next.js para ejecutar conversiones y visualizar parámetros espaciales.' },
  { icon: CheckCircle2, title: 'VALIDACIÓN Y AJUSTE', text: 'Pruebas de fidelidad sonora, normalización, loudness y procesamiento por bloques para optimizar la calidad de salida.' },
]

const autores = ['Sharon Catalina Vargas Cortes', 'Anwar Andrés Cuello Pabón']

export default function AcercaPage() {
  return (
    <div className="bg-aurora">
      <section className="mx-auto max-w-6xl px-6 pt-12 pb-14">
        <div className="grid lg:grid-cols-[0.85fr_1.15fr] gap-10 items-center">
          <div className="flex flex-col justify-center">
            <div className="self-start mb-6">
              <span className="inline-flex items-center gap-2 rounded-full border border-border bg-secondary/60 px-3 py-1 text-[11px] font-bold text-muted-foreground uppercase tracking-widest">
                PROYECTO DE INGENIERÍA ELECTRÓNICA
              </span>
            </div>
            <h1 className="text-balance text-4xl font-semibold tracking-tight sm:text-5xl mb-6">
              El proyecto Ambisonic
            </h1>
            <p className="text-pretty text-justify text-base sm:text-lg leading-relaxed text-muted-foreground mb-4">
              Ambisonic es una plataforma de audio espacial desarrollada desde un enfoque de Ingeniería Electrónica y Procesamiento Digital de Señales. Integra Ambisonics de primer orden, procesamiento estéreo y multicanal, y renderizado binaural mediante HRTF.
            </p>
            <p className="text-pretty text-justify text-base sm:text-lg leading-relaxed text-muted-foreground mb-8">
              Su motor DSP en Python se integra con FastAPI y Next.js para ejecutar conversiones, visualizar parámetros espaciales y generar diferentes formatos de salida desde una interfaz web.
            </p>
          </div>

          <Reveal delay={0.1} className="w-full justify-self-end">
            <img 
              src="/about-hero.png" 
              alt="Ambisonic"
              className="w-full h-[370px] object-cover rounded-3xl"
            />
          </Reveal>
        </div>

        {/* Timeline */}
        <div className="mt-12 w-full overflow-hidden lg:overflow-visible mx-auto max-w-7xl py-16">
          <h2 className="text-2xl font-semibold tracking-tight mx-auto max-w-6xl px-6 lg:px-0">Trayectoria</h2>

          {/* Versión Escritorio: Horizontal */}
          <div className="relative mt-16 hidden lg:block mx-auto max-w-7xl">
            <div className="grid grid-cols-5 grid-rows-[190px_70px_190px] gap-x-5 relative">
              {/* LÍNEA HORIZONTAL CONTINUA (ÚNICA) */}
              <div className="absolute left-0 right-0 top-[225px] h-[2px] bg-primary"></div>
              
              {timeline.map((item, i) => {
                const isTop = i % 2 === 0;
                return (
                  <React.Fragment key={item.title}>
                    {/* NODO Y CONECTOR VERTICAL (siempre en la fila 2) */}
                    <div className="col-start-auto row-start-2 flex flex-col items-center justify-center relative" style={{ gridColumn: i + 1 }}>
                      {/* Conector Vertical Corto */}
                      {isTop ? (
                        <div className="absolute bottom-[35px] w-[2px] h-[35px] bg-primary"></div>
                      ) : (
                        <div className="absolute top-[35px] w-[2px] h-[35px] bg-primary"></div>
                      )}
                      
                      {/* Nodo circular */}
                      <span className="relative z-10 flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground ring-4 ring-background shadow-[0_0_15px_rgba(124,58,237,0.5)]">
                        <item.icon className="h-4 w-4" />
                      </span>
                    </div>

                    {/* TARJETA (Fila 1 si es Top, Fila 3 si es Bottom) */}
                    {isTop ? (
                      <Reveal delay={i * 0.08} className="row-start-1 flex flex-col items-center justify-end w-full" style={{ gridColumn: i + 1 }}>
                        <div className="rounded-3xl glass border border-primary/30 p-5 w-full max-w-[210px] min-h-[135px] text-center shadow-xl mx-auto flex flex-col justify-center">
                          <h3 className="text-[11px] font-bold text-foreground uppercase tracking-wider mb-2 leading-tight">{item.title}</h3>
                          <p className="text-[11px] leading-relaxed text-muted-foreground">{item.text}</p>
                        </div>
                      </Reveal>
                    ) : (
                      <Reveal delay={i * 0.08} className="row-start-3 flex flex-col items-center justify-start w-full" style={{ gridColumn: i + 1 }}>
                        <div className="rounded-3xl glass border border-primary/30 p-5 w-full max-w-[210px] min-h-[135px] text-center shadow-xl mx-auto flex flex-col justify-center">
                          <h3 className="text-[11px] font-bold text-foreground uppercase tracking-wider mb-2 leading-tight">{item.title}</h3>
                          <p className="text-[11px] leading-relaxed text-muted-foreground">{item.text}</p>
                        </div>
                      </Reveal>
                    )}
                  </React.Fragment>
                )
              })}
            </div>
          </div>

          {/* Versión Móvil: Vertical */}
          <div className="relative mt-8 space-y-6 lg:hidden">
            {/* Línea vertical continua */}
            <div className="absolute left-[15px] top-9 bottom-9 w-[2px] bg-primary"></div>

            {timeline.map((item, i) => (
              <Reveal key={item.title} delay={i * 0.08}>
                <div className="relative flex items-start pl-14">
                  {/* Nodo circular */}
                  <span className="absolute left-0 top-5 z-10 flex h-8 w-8 items-center justify-center rounded-full bg-primary text-primary-foreground ring-4 ring-background shadow-[0_0_15px_rgba(124,58,237,0.5)]">
                    <item.icon className="h-4 w-4" />
                  </span>

                  {/* Línea horizontal de conexión */}
                  <div className="absolute left-8 top-[35px] w-6 h-[2px] bg-primary"></div>

                  {/* Tarjeta del hito */}
                  <div className="rounded-2xl glass border border-primary/30 p-5 w-full">
                    <h3 className="text-xs font-bold text-foreground uppercase tracking-wider mb-2">{item.title}</h3>
                    <p className="mt-1.5 text-[13px] leading-relaxed text-muted-foreground">{item.text}</p>
                  </div>
                </div>
              </Reveal>
            ))}
          </div>
        </div>

        {/* Créditos */}
        <Reveal className="mt-16">
          <div className="rounded-3xl glass p-6 sm:p-8">
            <h2 className="text-2xl font-semibold tracking-tight">Créditos</h2>
            <div className="mt-6 grid gap-4 sm:grid-cols-2">
              <div className="rounded-2xl border border-border bg-secondary/50 p-5 sm:col-span-2">
                <div className="flex items-center gap-2 text-primary">
                  <Users className="h-5 w-5" />
                  <span className="text-sm font-bold text-foreground">Autores</span>
                </div>
                <ul className="mt-3 grid gap-2 sm:grid-cols-2">
                  {autores.map((a) => (
                    <li key={a} className="text-sm font-bold text-foreground">
                      {a}
                    </li>
                  ))}
                </ul>
              </div>
              <CreditCard icon={UserCog} role="Director" name="Omar Javier Tíjaro Rojas" />
              <CreditCard icon={UserCog} role="Codirector" name="Nicolás Esteban Hernández Bustos" />
              <div className="flex items-center gap-4 rounded-2xl border border-primary/25 bg-primary/10 p-5 sm:col-span-2">
                <span className="flex h-12 w-12 shrink-0 items-center justify-center rounded-xl bg-primary text-primary-foreground">
                  <Building2 className="h-6 w-6" />
                </span>
                <div>
                  <div className="flex items-center gap-1.5 text-xs text-muted-foreground">
                    <GraduationCap className="h-4 w-4" /> Institución
                  </div>
                  <p className="mt-0.5 font-semibold text-foreground">Universidad Industrial de Santander</p>
                </div>
              </div>
            </div>
          </div>
        </Reveal>
      </section>
    </div>
  )
}

function CreditCard({
  icon: Icon,
  role,
  name,
}: {
  icon: React.ComponentType<{ className?: string }>
  role: string
  name: string
}) {
  return (
    <div className="rounded-2xl border border-border bg-secondary/50 p-5">
      <div className="flex items-center gap-2 text-primary">
        <Icon className="h-5 w-5" />
        <span className="text-xs font-bold uppercase tracking-wide text-foreground">{role}</span>
      </div>
      <p className="mt-2 font-bold text-foreground">{name}</p>
    </div>
  )
}
