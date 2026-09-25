'use client'

import React from 'react'
import {
  Headphones,
  Globe,
  Ear,
  ArrowRight,
  ArrowDown,
  Settings2,
  Move3d,
  Maximize,
  RefreshCcw,
  CheckCircle2,
  Activity,
  Layers,
  Cpu,
  Mic,
  GitMerge
} from 'lucide-react'
import { Reveal } from '@/components/reveal'

// Componentes gráficos

const AxesXYZ = () => (
  <div className="relative w-40 h-40 flex items-center justify-center my-8">
    <div className="absolute w-[2px] h-full bg-primary/30 flex flex-col justify-between items-center">
       <span className="text-[10px] -mt-5 font-mono text-primary font-bold">+Z (Arriba)</span>
       <span className="text-[10px] -mb-5 font-mono text-muted-foreground">-Z (Abajo)</span>
    </div>
    <div className="absolute h-[2px] w-full bg-primary/30 flex justify-between items-center">
       <span className="text-[10px] -ml-12 font-mono text-primary font-bold">+Y (Izq)</span>
       <span className="text-[10px] -mr-12 font-mono text-muted-foreground">-Y (Der)</span>
    </div>
    <div className="absolute w-[2px] h-[70%] bg-primary/30 rotate-45 flex flex-col justify-between items-center">
       <span className="text-[10px] -mt-5 -rotate-45 font-mono text-primary font-bold">+X (Frente)</span>
       <span className="text-[10px] -mb-5 -rotate-45 font-mono text-muted-foreground">-X (Atrás)</span>
    </div>
    <div className="w-3 h-3 rounded-full bg-primary z-10 shadow-[0_0_15px_rgba(124,58,237,1)]"></div>
  </div>
)

const FoaDiagram = () => (
  <div className="flex flex-col md:flex-row items-center gap-2 sm:gap-4 text-xs font-mono mt-6 w-full">
     <div className="glass p-3 rounded-xl border border-primary/30 flex flex-col items-center shrink-0 w-full md:w-auto">
        <span className="font-bold">FOA</span>
        <span className="text-primary">[W, X, Y, Z]</span>
     </div>
     <ArrowDown className="text-muted-foreground w-4 h-4 shrink-0 md:hidden" />
     <ArrowRight className="text-muted-foreground w-4 h-4 shrink-0 hidden md:block" />
     <div className="glass p-3 rounded-xl border border-border flex flex-col items-center shrink-0 w-full md:w-auto">
        <span className="font-bold">HRTF</span>
        <span className="text-muted-foreground">Filtros</span>
     </div>
     <ArrowDown className="text-muted-foreground w-4 h-4 shrink-0 md:hidden" />
     <ArrowRight className="text-muted-foreground w-4 h-4 shrink-0 hidden md:block" />
     <div className="glass p-3 rounded-xl border border-primary/30 flex flex-col items-center gap-2 shrink-0 w-full md:w-auto">
        <div className="flex gap-2 w-full">
           <span className="bg-secondary px-2 rounded font-bold flex-1 text-center py-1">Canal L</span>
           <span className="bg-secondary px-2 rounded font-bold flex-1 text-center py-1">Canal R</span>
        </div>
        <div className="flex items-center gap-2 text-primary">
          <Headphones className="w-4 h-4" />
          <span>Audífonos</span>
        </div>
     </div>
  </div>
)

const Option1Flow = () => (
  <div className="flex flex-col items-center gap-2 mt-6 text-xs font-mono w-full">
     <div className="glass px-6 py-2 rounded-xl border border-border w-full text-center">L + R</div>
     <ArrowDown className="text-muted-foreground w-4 h-4" />
     <div className="glass px-6 py-2 rounded-xl border border-primary/30 text-primary font-bold w-full text-center">procesamiento DSP</div>
     <ArrowDown className="text-muted-foreground w-4 h-4" />
     <div className="glass px-6 py-2 rounded-xl border border-border w-full text-center">W X Y Z</div>
     <ArrowDown className="text-muted-foreground w-4 h-4" />
     <div className="glass px-6 py-2 rounded-xl border border-primary/30 text-primary font-bold w-full text-center">binaural</div>
  </div>
)

const Option2Flow = () => (
  <div className="flex flex-col items-center gap-2 mt-6 text-xs font-mono w-full">
     <div className="glass px-6 py-2 rounded-xl border border-border w-full text-center">4 micrófonos</div>
     <ArrowDown className="text-muted-foreground w-4 h-4" />
     <div className="glass px-6 py-2 rounded-xl border border-border w-full text-center">4 señales (A-format)</div>
     <ArrowDown className="text-muted-foreground w-4 h-4" />
     <div className="glass px-6 py-2 rounded-xl border border-primary/30 text-primary font-bold w-full text-center">transformación</div>
     <ArrowDown className="text-muted-foreground w-4 h-4" />
     <div className="glass px-6 py-2 rounded-xl border border-border w-full text-center">B-format (W X Y Z)</div>
  </div>
)

const MatrixFlow = () => (
  <div className="flex flex-col md:flex-row items-center justify-center mt-8 text-xs font-mono w-full">
    <div className="flex flex-col gap-1 shrink-0 text-muted-foreground w-full md:w-auto">
      <div className="glass px-3 py-1 rounded border border-border text-center">[s1]</div>
      <div className="glass px-3 py-1 rounded border border-border text-center">[s2]</div>
      <div className="glass px-3 py-1 rounded border border-border text-center">[s3]</div>
      <div className="glass px-3 py-1 rounded border border-border text-center">[s4]</div>
    </div>
    <ArrowDown className="w-5 h-5 text-muted-foreground my-4 md:hidden shrink-0" />
    <ArrowRight className="w-5 h-5 text-muted-foreground mx-4 hidden md:block shrink-0" />
    <div className="glass px-4 py-3 rounded-xl border border-primary/50 text-primary font-bold shrink-0 text-center w-full md:w-auto">MATRIZ A → B</div>
    <ArrowDown className="w-5 h-5 text-muted-foreground my-4 md:hidden shrink-0" />
    <ArrowRight className="w-5 h-5 text-muted-foreground mx-4 hidden md:block shrink-0" />
    <div className="flex flex-col gap-1 shrink-0 text-foreground font-bold w-full md:w-auto">
      <div className="glass px-3 py-1 rounded border border-primary/30 text-center">W</div>
      <div className="glass px-3 py-1 rounded border border-primary/30 text-center">X</div>
      <div className="glass px-3 py-1 rounded border border-primary/30 text-center">Y</div>
      <div className="glass px-3 py-1 rounded border border-primary/30 text-center">Z</div>
    </div>
  </div>
)

const QuadMicFlowComplete = () => (
  <div className="flex flex-col items-center gap-3 text-xs font-mono text-center w-full max-w-sm mx-auto">
     <div className="glass px-6 py-3 rounded-2xl border border-border w-full">
        <span className="font-bold text-foreground">4 MICRÓFONOS</span>
     </div>
     <ArrowDown className="text-muted-foreground w-5 h-5" />
     
     <div className="glass px-6 py-3 rounded-2xl border border-border w-full">
        <span className="font-bold text-foreground">4 SEÑALES DE CÁPSULA</span>
     </div>
     <ArrowDown className="text-muted-foreground w-5 h-5" />
     
     <div className="glass px-6 py-3 rounded-2xl border border-border w-full">
        <span className="font-bold text-foreground tracking-widest">A-FORMAT</span>
     </div>
     <ArrowDown className="text-muted-foreground w-5 h-5" />
     
     <div className="glass px-6 py-3 rounded-2xl border border-primary/50 shadow-lg shadow-primary/10 w-full">
        <span className="text-primary font-bold">TRANSFORMACIÓN / CODIFICACIÓN</span>
     </div>
     <ArrowDown className="text-muted-foreground w-5 h-5" />
     
     <div className="glass px-6 py-3 rounded-2xl border border-primary/30 w-full">
        <span className="text-primary font-bold tracking-widest">B-FORMAT (FOA)</span>
     </div>
     <ArrowDown className="text-muted-foreground w-5 h-5" />
     
     <div className="glass px-6 py-3 rounded-2xl border border-border w-full text-foreground">
        <span className="font-bold tracking-widest">W · X · Y · Z</span>
     </div>
  </div>
)


export function GuiaContent() {
  return (
    <div className="bg-aurora pb-24">
      <style dangerouslySetInnerHTML={{__html: `html { scroll-behavior: smooth; }`}} />
      
      {/* 1. INTRODUCCIÓN Y TÍTULO */}
      <section className="mx-auto max-w-6xl px-6 pt-28 pb-12 sm:pt-32 text-center">
        <Reveal>
          <h1 className="text-balance text-4xl font-semibold tracking-tight sm:text-5xl">
            Guía del audio espacial
          </h1>
          <p className="mt-4 text-pretty text-lg leading-relaxed text-muted-foreground max-w-2xl mx-auto">
            Conceptos esenciales para comprender cómo Ambisonic representa, procesa y reproduce información espacial a partir de señales estéreo y multicanal.
          </p>
        </Reveal>
      </section>

      {/* ÍNDICE DE CONTENIDO */}
      <section className="mx-auto max-w-6xl px-6 pb-12">
        <Reveal delay={0.1}>
          <div className="glass p-8 rounded-3xl border border-primary/30 shadow-lg mx-auto max-w-4xl">
            <h2 className="text-xl font-bold mb-6 text-foreground">Contenido de la guía</h2>
            <div className="grid sm:grid-cols-2 md:grid-cols-3 gap-4">
              {[
                { id: 'conceptos', num: '01', title: 'Conceptos clave' },
                { id: 'opcion-1', num: '02', title: 'Opción 1 — Audio estéreo' },
                { id: 'opcion-2', num: '03', title: 'Opción 2 — Captura tetraédrica' },
                { id: 'demo', num: '04', title: 'Controles de la Demo' },
                { id: 'escucha', num: '05', title: 'Recomendaciones' },
              ].map((link) => (
                <a
                  key={link.id}
                  href={`#${link.id}`}
                  className="group flex items-start gap-3 p-3 rounded-2xl hover:bg-secondary/80 transition-colors border border-transparent hover:border-border"
                >
                  <span className="text-primary font-bold font-mono text-sm mt-0.5">{link.num}</span>
                  <span className="text-sm font-medium text-muted-foreground group-hover:text-foreground transition-colors leading-tight">
                    {link.title}
                  </span>
                </a>
              ))}
            </div>
          </div>
        </Reveal>
      </section>

      {/* 2. CONCEPTOS FUNDAMENTALES */}
      <section id="conceptos" className="mx-auto max-w-6xl px-6 py-12 scroll-mt-24">
        <Reveal>
          <h2 className="text-2xl font-semibold tracking-tight mb-8">Conceptos Fundamentales</h2>
        </Reveal>
        <div className="grid md:grid-cols-2 gap-6">
          <Reveal delay={0.1}>
            <div className="glass p-8 rounded-3xl border border-border h-full flex flex-col">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 rounded-xl bg-secondary/80 text-primary">
                  <Headphones className="w-5 h-5" />
                </div>
                <h3 className="text-lg font-bold">Audio estéreo</h3>
              </div>
              <p className="text-sm leading-relaxed text-muted-foreground flex-1">
                Una señal estéreo utiliza dos canales, izquierdo (L) y derecho (R), para representar diferencias de nivel, fase y contenido espectral entre ambos lados. Estas diferencias permiten percibir una distribución horizontal básica, pero no describen explícitamente un campo sonoro tridimensional.
              </p>
            </div>
          </Reveal>

          <Reveal delay={0.2}>
            <div className="glass p-8 rounded-3xl border border-primary/30 h-full flex flex-col shadow-lg shadow-primary/5">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 rounded-xl bg-primary/20 text-primary">
                  <Globe className="w-5 h-5" />
                </div>
                <h3 className="text-lg font-bold">Ambisonics de primer orden (FOA)</h3>
              </div>
              <p className="text-sm leading-relaxed text-muted-foreground">
                Ambisonics representa el campo sonoro mediante componentes matemáticas independientes de una configuración específica de reproducción. En primer orden se utilizan cuatro señales: W, X, Y y Z.
              </p>
              <div className="mt-4 grid grid-cols-2 gap-2 text-[11px] font-mono">
                <div className="bg-secondary/50 p-2 rounded border border-border"><span className="text-primary font-bold">W</span> → omnidireccional</div>
                <div className="bg-secondary/50 p-2 rounded border border-border"><span className="text-primary font-bold">X</span> → adelante / atrás</div>
                <div className="bg-secondary/50 p-2 rounded border border-border"><span className="text-primary font-bold">Y</span> → izquierda / derecha</div>
                <div className="bg-secondary/50 p-2 rounded border border-border"><span className="text-primary font-bold">Z</span> → arriba / abajo</div>
              </div>
            </div>
          </Reveal>

          <Reveal delay={0.3}>
            <div className="glass p-8 rounded-3xl border border-border h-full flex flex-col">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 rounded-xl bg-secondary/80 text-primary">
                  <Ear className="w-5 h-5" />
                </div>
                <h3 className="text-lg font-bold">Renderizado binaural mediante HRTF</h3>
              </div>
              <p className="text-sm leading-relaxed text-muted-foreground mb-4">
                Para reproducir el campo espacial mediante audífonos, las componentes ambisónicas se transforman a una señal binaural. El sistema utiliza respuestas al impulso relacionadas con la cabeza (HRTF), que modelan las diferencias de tiempo, nivel y respuesta espectral que llegan a cada oído dependiendo de la dirección de la fuente.
              </p>
              <FoaDiagram />
            </div>
          </Reveal>

          <Reveal delay={0.4}>
            <div className="glass p-8 rounded-3xl border border-border h-full flex flex-col relative overflow-hidden">
              <div className="flex items-center gap-3 mb-4">
                <div className="p-2 rounded-xl bg-secondary/80 text-primary">
                  <Globe className="w-5 h-5" />
                </div>
                <h3 className="text-lg font-bold">Coordenadas del sistema</h3>
              </div>
              <div className="flex flex-col sm:flex-row items-center justify-between gap-6">
                <div className="text-sm leading-relaxed text-muted-foreground flex-1">
                  <ul className="space-y-2 font-mono text-xs">
                    <li><span className="inline-block w-8 font-bold text-primary">+X</span> = frente</li>
                    <li><span className="inline-block w-8 font-bold text-muted-foreground">-X</span> = atrás</li>
                    <li><span className="inline-block w-8 font-bold text-primary">+Y</span> = izquierda</li>
                    <li><span className="inline-block w-8 font-bold text-muted-foreground">-Y</span> = derecha</li>
                    <li><span className="inline-block w-8 font-bold text-primary">+Z</span> = arriba</li>
                    <li><span className="inline-block w-8 font-bold text-muted-foreground">-Z</span> = abajo</li>
                  </ul>
                </div>
                <div className="flex-1 flex justify-center">
                  <AxesXYZ />
                </div>
              </div>
            </div>
          </Reveal>
        </div>
      </section>

      {/* DOS FORMAS DE USAR LA PLATAFORMA */}
      <section className="mx-auto max-w-6xl px-6 py-12">
        <Reveal>
          <div className="text-center mb-10">
             <h2 className="text-2xl font-semibold tracking-tight">Dos formas de usar la plataforma</h2>
          </div>
          <div className="grid md:grid-cols-2 gap-8">
             <div className="glass p-8 sm:p-10 rounded-[2rem] border border-primary/30 shadow-lg shadow-primary/5 h-full flex flex-col">
                <h3 className="text-base font-bold text-foreground mb-4 uppercase tracking-widest"><span className="text-primary mr-2">Opción 1</span> Audio estéreo</h3>
                <p className="text-sm text-muted-foreground leading-relaxed mb-8 flex-1">
                  Utiliza una grabación convencional de dos canales. El sistema procesa las señales L y R para construir una representación espacial FOA y posteriormente generar las salidas binaurales.
                </p>
                <div className="bg-secondary/30 p-6 rounded-2xl border border-border flex justify-center mt-auto">
                   <Option1Flow />
                </div>
             </div>

             <div className="glass p-8 sm:p-10 rounded-[2rem] border border-primary/30 shadow-lg shadow-primary/5 h-full flex flex-col">
                <h3 className="text-base font-bold text-foreground mb-4 uppercase tracking-widest"><span className="text-primary mr-2">Opción 2</span> Cuatro micrófonos</h3>
                <p className="text-sm text-muted-foreground leading-relaxed mb-8 flex-1">
                  Utiliza cuatro señales capturadas simultáneamente mediante un arreglo tetraédrico. La geometría y orientación de los micrófonos proporcionan información espacial que posteriormente se transforma a FOA.
                </p>
                <div className="bg-secondary/30 p-6 rounded-2xl border border-border flex justify-center mt-auto">
                   <Option2Flow />
                </div>
             </div>
          </div>
        </Reveal>
      </section>

      {/* 5. OPCIÓN 2 - DETALLE (NUEVA ESTRUCTURA) */}
      <section id="opcion-2" className="mx-auto max-w-6xl px-6 py-12 scroll-mt-24">
        <Reveal>
          <h2 className="text-2xl font-semibold tracking-tight mb-4">Representación física de la captura tetraédrica</h2>
          <p className="text-sm leading-relaxed text-muted-foreground mb-12 max-w-3xl">
             En la Opción 2 la información del espacio sonoro se captura físicamente desde la vida real utilizando una configuración especial.
          </p>

          <div className="w-full relative group mb-8 rounded-3xl border border-border shadow-lg bg-secondary/20 flex flex-col justify-center max-w-6xl mx-auto py-8">
            <img 
              src="/imagenmuestra.jpeg" 
              alt="Montaje arreglo tetraédrico" 
              className="w-full h-auto object-contain transition-transform duration-700"
            />
          </div>
          
          <p className="text-[11px] text-muted-foreground text-center italic mb-16 max-w-4xl mx-auto px-4">
             Figura — Representación conceptual de una configuración tetraédrica de cuatro micrófonos para captura multicanal. Se muestran las posiciones, orientaciones y vistas geométricas utilizadas para comprender la disposición espacial del arreglo.
          </p>

          <div className="glass p-8 rounded-3xl border border-primary/30 mb-16 shadow-lg max-w-4xl mx-auto">
            <h3 className="text-lg font-bold text-foreground mb-4">¿Qué representa este montaje?</h3>
            <p className="text-sm text-muted-foreground leading-relaxed mb-4">
              La figura muestra una posible implementación física de un arreglo tetraédrico de cuatro micrófonos. Cada cápsula se encuentra orientada hacia una dirección diferente y registra simultáneamente un canal independiente.
            </p>
            <p className="text-sm text-muted-foreground leading-relaxed">
              La disposición geométrica permite capturar variaciones del campo sonoro desde diferentes orientaciones, proporcionando la información necesaria para construir posteriormente una representación Ambisonics.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8 mb-16">
            <div className="glass p-8 rounded-3xl border border-border flex flex-col">
               <h3 className="text-lg font-bold text-foreground mb-4">A-format y B-format</h3>
               <p className="text-sm text-muted-foreground leading-relaxed mb-4">
                 <span className="font-bold text-foreground">A-format</span> representa las señales individuales obtenidas directamente de las cápsulas del arreglo tetraédrico. Estas señales todavía dependen de la geometría y orientación física del sistema de captura.
               </p>
               <p className="text-sm text-muted-foreground leading-relaxed flex-1">
                 <span className="font-bold text-foreground">B-format</span> es la representación Ambisonics obtenida después de transformar las señales A-format. En Ambisonics de primer orden (FOA), esta representación está formada por las componentes W, X, Y y Z, que describen el campo sonoro mediante una componente omnidireccional y tres componentes espaciales.
               </p>
            </div>
            
            <div className="glass p-8 rounded-3xl border border-border flex flex-col">
               <h3 className="text-lg font-bold text-foreground mb-4">¿Cómo se obtiene W, X, Y y Z?</h3>
               <p className="text-sm text-muted-foreground leading-relaxed flex-1">
                 Una matriz de transformación determina cómo contribuye cada una de las cuatro señales a las componentes W, X, Y y Z de Ambisonics de primer orden.
               </p>
               <div className="bg-secondary/30 rounded-2xl border border-border p-4 flex justify-center mt-6">
                 <MatrixFlow />
               </div>
            </div>
          </div>

          <div className="glass p-6 sm:p-10 rounded-[2rem] border border-primary/50 shadow-lg shadow-primary/10 bg-secondary/10">
             <h4 className="text-sm font-bold mb-10 text-center uppercase text-foreground tracking-widest">Flujo completo de conversión</h4>
             <QuadMicFlowComplete />
          </div>
        </Reveal>
      </section>

      {/* 6. CONTROLES DE LA DEMO */}
      <section id="demo" className="mx-auto max-w-6xl px-6 py-12 scroll-mt-24">
        <Reveal>
          <div className="text-center mb-12">
            <h2 className="text-2xl font-semibold tracking-tight">Controles de la Demo</h2>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="glass p-8 rounded-3xl border border-border flex flex-col hover:border-primary/50 transition-colors group">
              <h3 className="font-bold mb-4 flex items-center gap-2">DIRECCIÓN</h3>
              <p className="text-sm text-muted-foreground leading-relaxed flex-1 mb-8">
                Define la posición horizontal de referencia de la fuente sonora alrededor del oyente.
              </p>
              <ul className="text-xs font-mono mt-auto space-y-2 text-muted-foreground bg-secondary/50 p-4 rounded-xl border border-border">
                <li className="flex justify-between items-center"><span className="text-foreground font-bold">0°</span> <span>frente</span></li>
                <li className="flex justify-between items-center"><span className="text-foreground font-bold">+90°</span> <span>izquierda</span></li>
                <li className="flex justify-between items-center"><span className="text-foreground font-bold">−90°</span> <span>derecha</span></li>
              </ul>
            </div>

            <div className="glass p-8 rounded-3xl border border-border flex flex-col hover:border-primary/50 transition-colors group">
              <h3 className="font-bold mb-4 flex items-center gap-2">ALTURA</h3>
              <p className="text-sm text-muted-foreground leading-relaxed flex-1">
                Controla la componente vertical de la representación espacial y permite variar la percepción entre posiciones inferiores y superiores.
              </p>
            </div>

            <div className="glass p-8 rounded-3xl border border-border flex flex-col hover:border-primary/50 transition-colors group">
              <h3 className="font-bold mb-4 flex items-center gap-2">APERTURA</h3>
              <p className="text-sm text-muted-foreground leading-relaxed flex-1">
                Controla qué tan concentrada o extendida se percibe la escena sonora. Una apertura mayor produce una representación espacial más amplia.
              </p>
            </div>

            <div className="glass p-8 rounded-3xl border border-primary/30 shadow-lg shadow-primary/5 flex flex-col hover:border-primary transition-colors group">
              <h3 className="font-bold mb-4 flex items-center gap-2 text-primary">MOVIMIENTO</h3>
              <p className="text-sm text-muted-foreground leading-relaxed flex-1">
                Controla la intensidad de la variación temporal de la posición espacial alrededor de su referencia inicial.
              </p>
            </div>
          </div>
        </Reveal>
      </section>

      {/* 7. RECOMENDACIONES DE ESCUCHA */}
      <section id="escucha" className="mx-auto max-w-5xl px-6 py-12 mb-12 scroll-mt-24">
        <Reveal>
          <div className="glass p-8 sm:p-12 rounded-[2.5rem] border border-border relative overflow-hidden text-center">
            <h2 className="text-2xl font-semibold tracking-tight mb-10">Recomendaciones</h2>
            <div className="grid sm:grid-cols-2 gap-8 relative z-10 max-w-3xl mx-auto">
              <div className="flex flex-col items-center">
                <div className="w-12 h-12 rounded-full bg-secondary border border-border flex items-center justify-center text-foreground mb-4">
                   <Headphones className="w-5 h-5" />
                </div>
                <h4 className="font-bold text-base mb-3">AUDÍFONOS</h4>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  El renderizado binaural está diseñado principalmente para evaluación mediante audífonos.
                </p>
              </div>
              <div className="flex flex-col items-center">
                <div className="w-12 h-12 rounded-full bg-primary/20 border border-primary/30 flex items-center justify-center text-primary mb-4">
                   <CheckCircle2 className="w-5 h-5" />
                </div>
                <h4 className="font-bold text-base mb-3">COMPARACIÓN</h4>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  Puede compararse el audio original con las versiones binaural y 3D perceptual para identificar los cambios introducidos por el procesamiento.
                </p>
              </div>
            </div>
          </div>
        </Reveal>
      </section>
    </div>
  )
}
