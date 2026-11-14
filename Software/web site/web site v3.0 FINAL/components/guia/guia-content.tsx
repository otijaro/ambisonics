'use client'

import React, { useState } from 'react'
import {
  Headphones,
  Globe,
  Ear,
  ArrowRight,
  ArrowDown,
  Maximize,
  X,
  CheckCircle2,
  Layers,
  Cpu,
  Mic,
  GitMerge,
  Compass,
  MoveVertical,
  RefreshCw,
  Download,
  History,
  Clock,
  Sparkles,
  UserCheck,
  Radio,
  Sliders,
  Volume2,
} from 'lucide-react'
import { Reveal } from '@/components/reveal'

// =========================================================================
// COMPONENTES GRÁFICOS Y DIAGRAMAS (SIN DESBORDAMIENTOS NI VALORES NEGATIVOS)
// =========================================================================

const AxesXYZ = () => (
  <div className="w-full flex flex-col items-center justify-center my-2 select-none">
    <svg
      viewBox="0 0 360 260"
      className="w-full max-w-[340px] sm:max-w-[380px] h-auto overflow-visible"
    >
      <defs>
        {/* Marcadores de flechas */}
        <marker id="arrow-primary" markerWidth="7" markerHeight="7" refX="4" refY="3.5" orient="auto">
          <polygon points="0 0, 7 3.5, 0 7" fill="#7c3aed" />
        </marker>
        <marker id="arrow-muted" markerWidth="7" markerHeight="7" refX="4" refY="3.5" orient="auto">
          <polygon points="0 0, 7 3.5, 0 7" fill="#71717a" />
        </marker>
        {/* Gradiente radial para el resplandor central */}
        <radialGradient id="center-glow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#7c3aed" stopOpacity="0.55" />
          <stop offset="100%" stopColor="#7c3aed" stopOpacity="0" />
        </radialGradient>
      </defs>

      {/* Círculo base horizontal en perspectiva isométrica (elipse azimutal 360°) */}
      <ellipse
        cx="180"
        cy="130"
        rx="105"
        ry="38"
        fill="none"
        stroke="rgba(124, 58, 237, 0.22)"
        strokeWidth="1.5"
        strokeDasharray="4 4"
      />

      {/* --- EJE Z: VERTICAL (Arriba / Abajo) --- */}
      {/* -Z (Abajo) */}
      <line
        x1="180"
        y1="130"
        x2="180"
        y2="215"
        stroke="#71717a"
        strokeWidth="2"
        strokeDasharray="3 3"
        markerEnd="url(#arrow-muted)"
      />
      {/* +Z (Arriba) */}
      <line
        x1="180"
        y1="130"
        x2="180"
        y2="42"
        stroke="#7c3aed"
        strokeWidth="2.5"
        markerEnd="url(#arrow-primary)"
      />

      {/* --- EJE Y: LATERAL (Izquierda / Derecha) --- */}
      {/* -Y (Derecha) */}
      <line
        x1="180"
        y1="130"
        x2="288"
        y2="130"
        stroke="#71717a"
        strokeWidth="2"
        strokeDasharray="3 3"
        markerEnd="url(#arrow-muted)"
      />
      {/* +Y (Izquierda) */}
      <line
        x1="180"
        y1="130"
        x2="72"
        y2="130"
        stroke="#7c3aed"
        strokeWidth="2.5"
        markerEnd="url(#arrow-primary)"
      />

      {/* --- EJE X: FRONTAL (Adelante / Atrás en perspectiva) --- */}
      {/* -X (Atrás) */}
      <line
        x1="180"
        y1="130"
        x2="248"
        y2="78"
        stroke="#71717a"
        strokeWidth="2"
        strokeDasharray="3 3"
        markerEnd="url(#arrow-muted)"
      />
      {/* +X (Frente) */}
      <line
        x1="180"
        y1="130"
        x2="108"
        y2="185"
        stroke="#7c3aed"
        strokeWidth="2.5"
        markerEnd="url(#arrow-primary)"
      />

      {/* Resplandor y nodo central (Oyente en origen 0,0,0) */}
      <circle cx="180" cy="130" r="16" fill="url(#center-glow)" />
      <circle cx="180" cy="130" r="5.5" fill="#7c3aed" stroke="#ffffff" strokeWidth="1.5" />
      <text x="180" y="146" textAnchor="middle" fill="#a1a1aa" fontSize="9" fontFamily="monospace">
        Oyente (0,0,0)
      </text>

      {/* ETIQUETAS +Z / -Z (Con micro-tarjetas oscuras de alto contraste) */}
      <rect x="135" y="16" width="90" height="19" rx="5" fill="#18181b" stroke="#7c3aed" strokeWidth="1" />
      <text x="180" y="29.5" textAnchor="middle" fill="#c4b5fd" fontSize="10" fontFamily="monospace" fontWeight="bold">
        +Z Arriba (Cenit)
      </text>

      <rect x="135" y="223" width="90" height="19" rx="5" fill="#18181b" stroke="#3f3f46" strokeWidth="1" />
      <text x="180" y="236.5" textAnchor="middle" fill="#a1a1aa" fontSize="10" fontFamily="monospace">
        -Z Abajo (Nadir)
      </text>

      {/* ETIQUETAS +Y / -Y */}
      <rect x="6" y="120" width="60" height="19" rx="5" fill="#18181b" stroke="#7c3aed" strokeWidth="1" />
      <text x="36" y="133.5" textAnchor="middle" fill="#c4b5fd" fontSize="10" fontFamily="monospace" fontWeight="bold">
        +Y Izq
      </text>

      <rect x="294" y="120" width="60" height="19" rx="5" fill="#18181b" stroke="#3f3f46" strokeWidth="1" />
      <text x="324" y="133.5" textAnchor="middle" fill="#a1a1aa" fontSize="10" fontFamily="monospace">
        -Y Der
      </text>

      {/* ETIQUETAS +X / -X */}
      <rect x="44" y="187" width="76" height="19" rx="5" fill="#18181b" stroke="#7c3aed" strokeWidth="1" />
      <text x="82" y="200.5" textAnchor="middle" fill="#c4b5fd" fontSize="10" fontFamily="monospace" fontWeight="bold">
        +X Frente (0°)
      </text>

      <rect x="246" y="58" width="76" height="19" rx="5" fill="#18181b" stroke="#3f3f46" strokeWidth="1" />
      <text x="284" y="71.5" textAnchor="middle" fill="#a1a1aa" fontSize="10" fontFamily="monospace">
        -X Atrás (180°)
      </text>
    </svg>
  </div>
)

const FoaDiagram = () => (
  <div className="w-full mt-4 bg-secondary/30 rounded-2xl p-4 border border-border">
    <div className="flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-2.5 text-center">
      {/* Paso 1: FOA */}
      <div className="flex-1 min-w-0 glass p-2.5 sm:p-3 rounded-xl border border-primary/30 flex flex-col items-center justify-center">
        <span className="text-xs font-bold text-foreground">1. Campo FOA</span>
        <span className="text-[10px] font-mono text-primary font-semibold mt-0.5 truncate max-w-full">
          AmbiX [W, Y, Z, X]
        </span>
        <span className="text-[9px] text-muted-foreground mt-0.5 font-mono">Norm. SN3D</span>
      </div>

      <div className="flex justify-center sm:block shrink-0">
        <ArrowRight className="w-4 h-4 text-primary shrink-0 hidden sm:block" />
        <ArrowDown className="w-4 h-4 text-primary shrink-0 sm:hidden" />
      </div>

      {/* Paso 2: SAD */}
      <div className="flex-1 min-w-0 glass p-2.5 sm:p-3 rounded-xl border border-border flex flex-col items-center justify-center">
        <span className="text-xs font-bold text-foreground">2. Decodificador SAD</span>
        <span className="text-[10px] text-primary font-semibold mt-0.5 truncate max-w-full">
          6 Altavoces virtuales
        </span>
        <span className="text-[9px] text-muted-foreground mt-0.5 font-mono">HRIR SADIE II (D1)</span>
      </div>

      <div className="flex justify-center sm:block shrink-0">
        <ArrowRight className="w-4 h-4 text-primary shrink-0 hidden sm:block" />
        <ArrowDown className="w-4 h-4 text-primary shrink-0 sm:hidden" />
      </div>

      {/* Paso 3: Binaural */}
      <div className="flex-1 min-w-0 glass p-2.5 sm:p-3 rounded-xl border border-primary/30 flex flex-col items-center justify-center">
        <span className="text-xs font-bold text-foreground">3. Salida Binaural</span>
        <div className="flex items-center gap-1 text-primary text-[10px] font-semibold mt-0.5">
          <Headphones className="w-3 h-3 shrink-0" />
          <span>Canales L y R</span>
        </div>
        <span className="text-[9px] text-muted-foreground mt-0.5">Para audífonos</span>
      </div>
    </div>
    <p className="text-[11px] text-muted-foreground text-center mt-3 italic leading-snug">
      Flujo de renderizado: las 4 componentes esféricas se decodifican a 6 puntos virtuales octaédricos y se convolucionan con filtros HRIR.
    </p>
  </div>
)

const Option1Flow = () => (
  <div className="flex flex-col items-center gap-2 mt-4 text-xs font-mono w-full max-w-sm mx-auto">
    <div className="glass px-4 py-2 rounded-xl border border-border w-full text-center text-foreground font-medium">
      Audio Estéreo (Canales L + R)
    </div>
    <ArrowDown className="text-muted-foreground w-4 h-4 shrink-0" />
    <div className="glass px-4 py-2 rounded-xl border border-primary/30 text-primary font-bold w-full text-center">
      Análisis Espectral STFT + Coherencia MSC
    </div>
    <ArrowDown className="text-muted-foreground w-4 h-4 shrink-0" />
    <div className="glass px-4 py-2 rounded-xl border border-border w-full text-center text-foreground font-medium">
      FOA AmbiX [W, Y, Z, X] (Side preservado en Y)
    </div>
    <ArrowDown className="text-muted-foreground w-4 h-4 shrink-0" />
    <div className="glass px-4 py-2 rounded-xl border border-primary/30 text-primary font-bold w-full text-center">
      Decodificación SAD → Salidas Binaurales
    </div>
  </div>
)

const Option2Flow = () => (
  <div className="flex flex-col items-center gap-2 mt-4 text-xs font-mono w-full max-w-sm mx-auto">
    <div className="glass px-4 py-2 rounded-xl border border-border w-full text-center text-foreground font-medium">
      4 Micrófonos (Arreglo Tetraédrico)
    </div>
    <ArrowDown className="text-muted-foreground w-4 h-4 shrink-0" />
    <div className="glass px-4 py-2 rounded-xl border border-border w-full text-center text-foreground font-medium">
      Formato A: Cápsulas [FLU, FRD, BLD, BRU]
    </div>
    <ArrowDown className="text-muted-foreground w-4 h-4 shrink-0" />
    <div className="glass px-4 py-2 rounded-xl border border-primary/30 text-primary font-bold w-full text-center">
      Matriz Ortogonal Tetraédrica
    </div>
    <ArrowDown className="text-muted-foreground w-4 h-4 shrink-0" />
    <div className="glass px-4 py-2 rounded-xl border border-border w-full text-center text-foreground font-medium">
      Formato B: FOA AmbiX [W, Y, Z, X]
    </div>
  </div>
)

const MatrixFlow = () => (
  <div className="flex flex-col sm:flex-row items-center justify-center gap-3 sm:gap-4 my-3 text-xs font-mono w-full">
    {/* Entradas */}
    <div className="grid grid-cols-2 sm:grid-cols-1 gap-1.5 shrink-0 text-muted-foreground text-center">
      <div className="glass px-2.5 py-1 rounded border border-border text-[11px]">[FLU]</div>
      <div className="glass px-2.5 py-1 rounded border border-border text-[11px]">[FRD]</div>
      <div className="glass px-2.5 py-1 rounded border border-border text-[11px]">[BLD]</div>
      <div className="glass px-2.5 py-1 rounded border border-border text-[11px]">[BRU]</div>
    </div>

    <ArrowRight className="w-5 h-5 text-muted-foreground shrink-0 hidden sm:block" />
    <ArrowDown className="w-5 h-5 text-muted-foreground shrink-0 sm:hidden" />

    {/* Matriz */}
    <div className="glass px-4 py-3 rounded-xl border border-primary/50 text-primary font-bold shrink-0 text-center">
      MATRIZ TETRAÉDRICA
      <span className="block text-[10px] text-muted-foreground font-normal mt-0.5">Transformación A → B</span>
    </div>

    <ArrowRight className="w-5 h-5 text-muted-foreground shrink-0 hidden sm:block" />
    <ArrowDown className="w-5 h-5 text-muted-foreground shrink-0 sm:hidden" />

    {/* Salidas */}
    <div className="grid grid-cols-2 sm:grid-cols-1 gap-1.5 shrink-0 text-foreground font-bold text-center">
      <div className="glass px-2.5 py-1 rounded border border-primary/30 text-[11px]">W (Omni)</div>
      <div className="glass px-2.5 py-1 rounded border border-primary/30 text-[11px]">Y (Lateral)</div>
      <div className="glass px-2.5 py-1 rounded border border-primary/30 text-[11px]">Z (Vertical)</div>
      <div className="glass px-2.5 py-1 rounded border border-primary/30 text-[11px]">X (Frontal)</div>
    </div>
  </div>
)

const QuadMicFlowComplete = () => (
  <div className="flex flex-col items-center gap-2.5 text-xs font-mono text-center w-full max-w-sm mx-auto">
    <div className="glass px-5 py-2.5 rounded-2xl border border-border w-full">
      <span className="font-bold text-foreground">4 MICRÓFONOS TETRAÉDRICOS</span>
    </div>
    <ArrowDown className="text-muted-foreground w-4 h-4 shrink-0" />

    <div className="glass px-5 py-2.5 rounded-2xl border border-border w-full">
      <span className="font-bold text-foreground text-[11px]">CÁPSULAS: FLU · FRD · BLD · BRU</span>
    </div>
    <ArrowDown className="text-muted-foreground w-4 h-4 shrink-0" />

    <div className="glass px-5 py-2.5 rounded-2xl border border-border w-full">
      <span className="font-bold text-foreground tracking-wider">FORMATO A (A-FORMAT)</span>
    </div>
    <ArrowDown className="text-muted-foreground w-4 h-4 shrink-0" />

    <div className="glass px-5 py-2.5 rounded-2xl border border-primary/50 shadow-md shadow-primary/10 w-full">
      <span className="text-primary font-bold">TRANSFORMACIÓN MATRICIAL ORTOGONAL</span>
    </div>
    <ArrowDown className="text-muted-foreground w-4 h-4 shrink-0" />

    <div className="glass px-5 py-2.5 rounded-2xl border border-primary/30 w-full">
      <span className="text-primary font-bold tracking-wider">FORMATO B (FOA AmbiX)</span>
    </div>
    <ArrowDown className="text-muted-foreground w-4 h-4 shrink-0" />

    <div className="glass px-5 py-2.5 rounded-2xl border border-border w-full text-foreground">
      <span className="font-bold tracking-widest">W · Y · Z · X (SN3D)</span>
    </div>
  </div>
)

// =========================================================================
// CONTENIDO PRINCIPAL DE LA GUÍA
// =========================================================================

export function GuiaContent() {
  const [isImageOpen, setIsImageOpen] = useState(false)

  const indexSections = [
    { id: 'conceptos', num: '01', title: 'Conceptos clave' },
    { id: 'formatos-salidas', num: '02', title: 'Formatos y salidas' },
    { id: 'opcion-1', num: '03', title: 'Opción 1: Estéreo' },
    { id: 'opcion-2', num: '04', title: 'Opción 2: 4 micrófonos' },
    { id: 'demo', num: '05', title: 'Demo interactiva' },
    { id: 'conversiones', num: '06', title: 'Mis conversiones' },
    { id: 'acronimos', num: '07', title: 'Glosario de siglas' },
    { id: 'escucha', num: '08', title: 'Recomendaciones' },
  ]

  return (
    <div className="bg-aurora min-h-screen pb-24 text-foreground overflow-x-hidden">
      <style dangerouslySetInnerHTML={{ __html: `html { scroll-behavior: smooth; }` }} />

      {/* 1. ENCABEZADO Y TÍTULO — ALINEACIÓN CONSISTENTE */}
      <section className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 pt-24 pb-8 sm:pt-28">
        <Reveal>
          <div className="max-w-3xl">
            <span className="inline-flex items-center gap-2 rounded-full border border-primary/30 bg-primary/10 px-3.5 py-1 text-xs text-primary font-semibold uppercase tracking-wider mb-4">
              Documentación técnica
            </span>
            <h1 className="text-balance text-3xl font-bold tracking-tight sm:text-5xl text-foreground">
              Guía del Audio Espacial
            </h1>
            <p className="mt-4 text-pretty text-base sm:text-lg leading-relaxed text-muted-foreground">
              Aprende cómo la plataforma Ambisonic transforma señales de audio estéreo y multicanal en campos sonoros tridimensionales envolventes mediante Ambisonics y renderizado binaural.
            </p>
          </div>
        </Reveal>
      </section>

      {/* ÍNDICE DE CONTENIDO — DISTRIBUCIÓN BALANCEADA EXACTA 4 ARRIBA Y 4 ABAJO */}
      <section className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 pb-10">
        <Reveal delay={0.1}>
          <div className="glass p-5 sm:p-6 rounded-3xl border border-primary/30 shadow-lg w-full">
            <div className="flex items-center justify-between gap-4 mb-4 pb-3 border-b border-border/60">
              <h2 className="text-sm sm:text-base font-bold text-foreground">Navegación de la guía</h2>
            </div>
            {/* Grid simétrico 4 x 2: 4 columnas en desktop, 2 en móviles */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 sm:gap-4">
              {indexSections.map((item) => (
                <a
                  key={item.id}
                  href={`#${item.id}`}
                  className="group flex flex-col p-3 sm:p-3.5 rounded-2xl bg-secondary/30 hover:bg-secondary/70 border border-border/80 hover:border-primary/40 transition-all duration-200"
                >
                  <span className="text-primary font-bold font-mono text-xs mb-1">{item.num}</span>
                  <span className="text-xs sm:text-sm font-medium text-foreground group-hover:text-primary transition-colors leading-snug">
                    {item.title}
                  </span>
                </a>
              ))}
            </div>
          </div>
        </Reveal>
      </section>

      {/* 2. CONCEPTOS FUNDAMENTALES */}
      <section id="conceptos" className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-10 scroll-mt-24">
        <Reveal>
          <div className="mb-8">
            <h2 className="text-2xl font-bold tracking-tight text-foreground">01. Conceptos Fundamentales</h2>
            <p className="text-sm text-muted-foreground mt-1">
              Bases teóricas de la reproducción y codificación de campos acústicos espaciales.
            </p>
          </div>
        </Reveal>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Tarjeta 1: Audio Estéreo */}
          <Reveal delay={0.1}>
            <div className="glass p-6 sm:p-7 rounded-3xl border border-border h-full flex flex-col justify-between">
              <div>
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-2.5 rounded-xl bg-secondary text-primary">
                    <Headphones className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-foreground">Audio Estéreo Convencional</h3>
                    <span className="text-xs text-muted-foreground">2 canales: Izquierdo (L) y Derecho (R)</span>
                  </div>
                </div>
                <p className="text-sm leading-relaxed text-muted-foreground">
                  El formato estéreo convencional representa el sonido a través de dos canales frontales independientes: <strong>L</strong> (<em>Left</em> / Izquierdo) y <strong>R</strong> (<em>Right</em> / Derecho). Genera una imagen horizontal básica basada en diferencias de amplitud y tiempo entre ambos oídos, pero carece de información sobre la elevación vertical (arriba/abajo) o la profundidad posterior (adelante/atrás).
                </p>
              </div>
            </div>
          </Reveal>

          {/* Tarjeta 2: Ambisonics FOA */}
          <Reveal delay={0.2}>
            <div className="glass p-6 sm:p-7 rounded-3xl border border-primary/30 h-full flex flex-col justify-between shadow-lg shadow-primary/5">
              <div>
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-2.5 rounded-xl bg-primary/20 text-primary">
                    <Globe className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-foreground">Ambisonics de Primer Orden (FOA / AmbiX)</h3>
                    <span className="text-xs text-primary font-mono font-semibold">Orden ACN [W, Y, Z, X] · Convención SN3D</span>
                  </div>
                </div>
                <p className="text-sm leading-relaxed text-muted-foreground mb-4">
                  <strong>FOA</strong> (<em>First-Order Ambisonics</em>, o Ambisónicos de Primer Orden) bajo el estándar <strong>AmbiX</strong> describe una esfera acústica continua e independiente de los altavoces mediante cuatro componentes normalizadas en convención <strong>SN3D</strong> y orden numérico <strong>ACN</strong> (<em>Ambisonic Channel Number</em>):
                </p>
              </div>
              <div className="grid grid-cols-2 gap-2 text-xs font-mono mt-auto">
                <div className="bg-secondary/40 p-2.5 rounded-xl border border-border">
                  <span className="text-primary font-bold">W (Canal 0):</span> Omnidireccional (presión)
                </div>
                <div className="bg-secondary/40 p-2.5 rounded-xl border border-border">
                  <span className="text-primary font-bold">Y (Canal 1):</span> Lateral (izquierda / derecha)
                </div>
                <div className="bg-secondary/40 p-2.5 rounded-xl border border-border">
                  <span className="text-primary font-bold">Z (Canal 2):</span> Vertical (arriba / abajo)
                </div>
                <div className="bg-secondary/40 p-2.5 rounded-xl border border-border">
                  <span className="text-primary font-bold">X (Canal 3):</span> Frontal (adelante / atrás)
                </div>
              </div>
            </div>
          </Reveal>

          {/* Tarjeta 3: Decodificación SAD y HRIR */}
          <Reveal delay={0.3}>
            <div className="glass p-6 sm:p-7 rounded-3xl border border-border h-full flex flex-col justify-between overflow-hidden">
              <div>
                <div className="flex items-center gap-3 mb-4">
                  <div className="p-2.5 rounded-xl bg-secondary text-primary">
                    <Ear className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-foreground">Decodificación SAD y HRIR SADIE II D1</h3>
                    <span className="text-xs text-muted-foreground">Proyección binaural sobre 6 altavoces virtuales</span>
                  </div>
                </div>
                <p className="text-sm leading-relaxed text-muted-foreground">
                  Para escuchar la esfera Ambisonics con audífonos, el decodificador <strong>SAD</strong> (<em>Sampling Ambisonic Decoder</em>) proyecta analíticamente las 4 señales FOA sobre una <strong>Geometría B octaédrica</strong> de 6 altavoces virtuales en cruz simétrica. Cada altavoz se filtra mediante respuestas al impulso <strong>HRIR</strong> (<em>Head-Related Impulse Response</em>) de la base de datos <strong>SADIE II (sujeto D1)</strong>.
                </p>
              </div>
              {/* Diagrama con contención estricta para evitar sobreposiciones */}
              <div className="mt-4">
                <FoaDiagram />
              </div>
            </div>
          </Reveal>

          {/* Tarjeta 4: Coordenadas Espaciales */}
          <Reveal delay={0.4}>
            <div className="glass p-6 sm:p-7 rounded-3xl border border-border h-full flex flex-col justify-between overflow-hidden">
              <div>
                <div className="flex items-center gap-3 mb-3">
                  <div className="p-2.5 rounded-xl bg-secondary text-primary">
                    <Compass className="w-5 h-5" />
                  </div>
                  <div>
                    <h3 className="text-base font-bold text-foreground">Sistema de Coordenadas 3D</h3>
                    <span className="text-xs text-muted-foreground">Orientación espacial centrada en el oyente</span>
                  </div>
                </div>
                <p className="text-sm leading-relaxed text-muted-foreground">
                  El sistema posiciona los elementos acústicos en un espacio tridimensional centrado en la cabeza del oyente con respecto a los tres ejes cartesianos:
                </p>
              </div>

              {/* Diagrama SVG amplio y completamente legible */}
              <div className="my-2">
                <AxesXYZ />
              </div>

              {/* Resumen inferior de los tres ejes */}
              <div className="grid grid-cols-3 gap-2 text-center text-[11px] font-mono mt-auto pt-2 border-t border-border/60">
                <div className="bg-secondary/40 p-2 rounded-xl border border-border">
                  <span className="text-primary font-bold block">Eje X (Frontal)</span>
                  <span className="text-muted-foreground text-[10px]">0° Frente · 180° Atrás</span>
                </div>
                <div className="bg-secondary/40 p-2 rounded-xl border border-border">
                  <span className="text-primary font-bold block">Eje Y (Lateral)</span>
                  <span className="text-muted-foreground text-[10px]">±90° Izq / Der</span>
                </div>
                <div className="bg-secondary/40 p-2 rounded-xl border border-border">
                  <span className="text-primary font-bold block">Eje Z (Vertical)</span>
                  <span className="text-muted-foreground text-[10px]">±90° Cenit / Nadir</span>
                </div>
              </div>
            </div>
          </Reveal>
        </div>
      </section>

      {/* 3. FORMATOS, FRECUENCIAS Y ARCHIVOS DE SALIDA */}
      <section id="formatos-salidas" className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-10 scroll-mt-24">
        <Reveal>
          <div className="mb-8">
            <h2 className="text-2xl font-bold tracking-tight text-foreground">02. Formatos, Frecuencias y Archivos Generados</h2>
            <p className="text-sm text-muted-foreground mt-1">
              Requisitos de entrada y características de cada uno de los archivos resultantes.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div className="glass p-6 rounded-3xl border border-border flex flex-col justify-between">
              <div>
                <div className="flex items-center gap-3 mb-3">
                  <div className="p-2 rounded-xl bg-secondary text-primary">
                    <Radio className="w-5 h-5" />
                  </div>
                  <h3 className="text-base font-bold text-foreground">Formatos de Entrada</h3>
                </div>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  Admite archivos de audio <strong>WAV</strong> y <strong>MP3</strong>, tanto en estéreo convencional (2 canales) como en captura tetraédrica de 4 micrófonos.
                </p>
              </div>
            </div>

            <div className="glass p-6 rounded-3xl border border-primary/30 shadow-md shadow-primary/5 flex flex-col justify-between">
              <div>
                <div className="flex items-center gap-3 mb-3">
                  <div className="p-2 rounded-xl bg-primary/20 text-primary">
                    <Cpu className="w-5 h-5" />
                  </div>
                  <h3 className="text-base font-bold text-foreground">Frecuencias Nativas</h3>
                </div>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  Soporta estrictamente <strong>44,1 kHz</strong>, <strong>48 kHz</strong> y <strong>96 kHz</strong>. El procesamiento es exacto y sin remuestreo forzado, empleando perfiles HRIR medidos a cada tasa para evitar pérdidas espectrales.
                </p>
              </div>
            </div>

            <div className="glass p-6 rounded-3xl border border-border flex flex-col justify-between">
              <div>
                <div className="flex items-center gap-3 mb-3">
                  <div className="p-2 rounded-xl bg-secondary text-primary">
                    <Download className="w-5 h-5" />
                  </div>
                  <h3 className="text-base font-bold text-foreground">Descargas Directas</h3>
                </div>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  La plataforma genera archivos en <strong>WAV</strong> (PCM 16 bits sin pérdidas), <strong>MP3</strong> (320 kbps para escucha ágil) y el archivo espacial <strong>FOA de 4 canales</strong> para uso profesional.
                </p>
              </div>
            </div>
          </div>

          {/* Tarjeta Comparativa de las 3 Salidas */}
          <div className="glass p-6 sm:p-8 rounded-3xl border border-border">
            <h3 className="text-base font-bold text-foreground mb-4">¿En qué se diferencian las 3 salidas del Conversor?</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
              <div className="p-5 rounded-2xl bg-secondary/30 border border-border flex flex-col justify-between">
                <div>
                  <div className="flex items-center gap-2 text-primary font-bold text-sm mb-1.5">
                    <Headphones className="w-4 h-4" />
                    <span>Binaural Estándar</span>
                  </div>
                  <span className="text-[11px] font-mono text-muted-foreground mb-3 block">2 canales (L / R) · WAV y MP3</span>
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    Audio binaural generado mediante el decodificador SAD y las respuestas impulsionales HRIR de SADIE II D1. Con un nivel máximo de amplitud controlado para evitar la saturación digital, listo para su reproducción con audífonos convencionales.
                  </p>
                </div>
              </div>

              <div className="p-5 rounded-2xl bg-secondary/30 border border-primary/30 flex flex-col justify-between">
                <div>
                  <div className="flex items-center gap-2 text-primary font-bold text-sm mb-1.5">
                    <Sparkles className="w-4 h-4" />
                    <span>Binaural 3D Perceptual</span>
                  </div>
                  <span className="text-[11px] font-mono text-muted-foreground mb-3 block">2 canales (L / R) · WAV y MP3</span>
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    Aplica una suave modulación espacial dinámica en órbita 3D y estabilización de sonoridad. Brinda una experiencia auditiva más envolvente y aireada para música y paisajes sonoros.
                  </p>
                </div>
              </div>

              <div className="p-5 rounded-2xl bg-secondary/30 border border-border flex flex-col justify-between">
                <div>
                  <div className="flex items-center gap-2 text-foreground font-bold text-sm mb-1.5">
                    <Layers className="w-4 h-4 text-primary" />
                    <span>Archivo FOA (AmbiX)</span>
                  </div>
                  <span className="text-[11px] font-mono text-primary font-bold mb-3 block">4 canales · WAV · [W, Y, Z, X]</span>
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    Archivo ambisónico maestro sin filtrar a binaural. Contiene la esfera espacial completa para postproducción en <strong>DAWs</strong> (<em>Digital Audio Workstations</em> como Reaper o Pro Tools), motores de videojuegos (Unity, Unreal) y video 360°/<strong>VR</strong> (<em>Virtual Reality</em>).
                  </p>
                </div>
              </div>
            </div>
          </div>
        </Reveal>
      </section>

      {/* 4. DOS FORMAS DE USAR LA PLATAFORMA */}
      <section className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-10">
        <Reveal>
          <div className="mb-8 text-center max-w-2xl mx-auto">
            <h2 className="text-2xl font-bold tracking-tight text-foreground">Dos Formas de Usar el Conversor</h2>
            <p className="text-sm text-muted-foreground mt-1">
              Selecciona el modo según el tipo de grabación disponible.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 sm:gap-8">
            {/* Opción 1 */}
            <div id="opcion-1" className="glass p-6 sm:p-8 rounded-[2rem] border border-primary/30 shadow-md shadow-primary/5 flex flex-col justify-between scroll-mt-24">
              <div>
                <div className="flex items-center gap-2.5 mb-3">
                  <span className="bg-primary/20 text-primary text-xs font-bold px-2.5 py-1 rounded-lg">OPCIÓN 1</span>
                  <h3 className="text-base font-bold text-foreground">Audio Estéreo Convencional</h3>
                </div>
                <p className="text-sm text-muted-foreground leading-relaxed mb-6">
                  Convierte canciones o audios estéreo estándar de dos canales. El procesador analiza el espectro en tiempo-frecuencia mediante <strong>STFT</strong> (<em>Short-Time Fourier Transform</em> a 2048 muestras), calcula la coherencia espectral local <strong>MSC</strong> (<em>Magnitude Squared Coherence</em> con ventana temporal de 100 ms) para distinguir sonidos directos de difusos, y preserva la componente lateral <em>Side</em> en el canal <span className="font-mono text-primary font-semibold">Y = S · cos(elevación)</span> para no perder información ante señales en oposición de fase.
                </p>
              </div>
              <div className="bg-secondary/30 p-5 rounded-2xl border border-border mt-auto">
                <Option1Flow />
              </div>
            </div>

            {/* Opción 2 */}
            <div id="opcion-2" className="glass p-6 sm:p-8 rounded-[2rem] border border-primary/30 shadow-md shadow-primary/5 flex flex-col justify-between scroll-mt-24">
              <div>
                <div className="flex items-center gap-2.5 mb-3">
                  <span className="bg-primary/20 text-primary text-xs font-bold px-2.5 py-1 rounded-lg">OPCIÓN 2</span>
                  <h3 className="text-base font-bold text-foreground">Captura de 4 Micrófonos (Tetraédrico)</h3>
                </div>
                <p className="text-sm text-muted-foreground leading-relaxed mb-6">
                  Diseñado para grabaciones reales con micrófonos ambisónicos de 4 cápsulas en configuración tetraédrica (<strong>formato A</strong> o <em>A-format</em>). Requiere los canales en el orden canónico <strong>FLU, FRD, BLD y BRU</strong>. La matriz ortogonal del sistema desacopla matemáticamente las señales en las componentes esféricas W, Y, Z y X (<strong>formato B</strong> o <em>B-format</em>) con exactitud física de campo libre.
                </p>
              </div>
              <div className="bg-secondary/30 p-5 rounded-2xl border border-border mt-auto">
                <Option2Flow />
              </div>
            </div>
          </div>
        </Reveal>
      </section>

      {/* 5. DETALLE DE CAPTURA TETRAÉDRICA */}
      <section id="opcion-2-detalle" className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-10">
        <Reveal>
          <div className="mb-6">
            <h2 className="text-2xl font-bold tracking-tight text-foreground">04. Detalle de la Captura Tetraédrica</h2>
            <p className="text-sm text-muted-foreground mt-1 max-w-3xl">
              Cómo se obtiene el campo espacial a partir de cuatro cápsulas físicas en el espacio real.
            </p>
          </div>

          {/* Contenedor de la imagen: ampliado en la página y con modal para zoom completo */}
          <div 
            onClick={() => setIsImageOpen(true)}
            className="w-full relative group mb-6 rounded-3xl border border-border/80 hover:border-primary/50 shadow-xl bg-secondary/20 flex flex-col justify-center max-w-5xl mx-auto p-4 sm:p-6 overflow-hidden cursor-pointer transition-all duration-300"
          >
            <div className="relative w-full flex items-center justify-center">
              <img 
                src="/imagenmuestra.jpeg" 
                alt="Montaje de arreglo tetraédrico de cuatro micrófonos" 
                className="w-full h-auto max-h-[520px] sm:max-h-[620px] object-contain mx-auto rounded-2xl group-hover:scale-[1.01] transition-transform duration-300"
              />
              <div className="absolute bottom-4 right-4 bg-background/85 backdrop-blur-md border border-border px-3 py-1.5 rounded-xl text-xs font-medium text-foreground flex items-center gap-1.5 shadow-lg group-hover:border-primary/50 transition-colors">
                <Maximize className="w-3.5 h-3.5 text-primary" />
                <span>Clic para ampliar</span>
              </div>
            </div>
          </div>

          {/* Modal / Lightbox para ver la imagen en tamaño completo */}
          {isImageOpen && (
            <div 
              className="fixed inset-0 z-50 bg-black/85 backdrop-blur-md flex items-center justify-center p-4 sm:p-8 animate-in fade-in duration-200"
              onClick={() => setIsImageOpen(false)}
            >
              <div className="relative max-w-5xl max-h-[92vh] w-full flex flex-col items-center justify-center">
                <button
                  type="button"
                  onClick={() => setIsImageOpen(false)}
                  className="absolute -top-12 right-0 sm:right-2 text-white/80 hover:text-white bg-white/10 hover:bg-white/20 p-2 rounded-full transition-colors cursor-pointer"
                  aria-label="Cerrar vista ampliada"
                >
                  <X className="w-5 h-5" />
                </button>
                <img 
                  src="/imagenmuestra.jpeg" 
                  alt="Montaje de arreglo tetraédrico ampliado" 
                  className="max-w-full max-h-[85vh] object-contain rounded-2xl border border-white/10 shadow-2xl"
                  onClick={(e) => e.stopPropagation()}
                />
                <span className="text-xs text-white/70 mt-3 font-mono">Presiona en cualquier lugar o en la cruz para cerrar</span>
              </div>
            </div>
          )}
          
          <p className="text-[11px] text-muted-foreground text-center italic mb-10 max-w-3xl mx-auto px-4">
            Figura — Configuración geométrica de cuatro micrófonos cardioides orientados en un tetraedro regular para captura multicanal en formato A. Haz clic sobre la imagen para ampliarla en alta resolución.
          </p>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div className="glass p-6 sm:p-7 rounded-3xl border border-border flex flex-col justify-between">
              <div>
                <h3 className="text-base font-bold text-foreground mb-3">Nomenclatura de las Cápsulas</h3>
                <p className="text-sm text-muted-foreground leading-relaxed mb-4">
                  Cada canal corresponde a la orientación espacial de una cápsula física:
                </p>
                <ul className="text-xs font-mono space-y-2 text-muted-foreground bg-secondary/40 p-4 rounded-xl border border-border">
                  <li><span className="text-primary font-bold">1. FLU:</span> Front-Left-Up (Frontal Izquierda Superior)</li>
                  <li><span className="text-primary font-bold">2. FRD:</span> Front-Right-Down (Frontal Derecha Inferior)</li>
                  <li><span className="text-primary font-bold">3. BLD:</span> Back-Left-Down (Posterior Izquierda Inferior)</li>
                  <li><span className="text-primary font-bold">4. BRU:</span> Back-Right-Up (Posterior Derecha Superior)</li>
                </ul>
              </div>
            </div>
            
            <div className="glass p-6 sm:p-7 rounded-3xl border border-border flex flex-col justify-between">
              <div>
                <h3 className="text-base font-bold text-foreground mb-3">Matriz de Transformación A → B</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  La matriz ortogonal tetraédrica M<sub>tetra</sub> pondera las cuatro señales para recomponer el patrón omnidireccional W y los tres dipolos ortogonales Y, Z y X que conforman el formato B:
                </p>
              </div>
              <div className="bg-secondary/30 rounded-2xl border border-border p-4 flex justify-center mt-4">
                <MatrixFlow />
              </div>
            </div>
          </div>

          <div className="glass p-6 sm:p-8 rounded-[2rem] border border-primary/50 shadow-md shadow-primary/10 bg-secondary/10">
            <h4 className="text-xs font-bold mb-6 text-center uppercase text-foreground tracking-widest">
              Flujo completo de conversión tetraédrica
            </h4>
            <QuadMicFlowComplete />
          </div>
        </Reveal>
      </section>

      {/* 6. CONTROLES DE LA DEMO INTERACTIVA — ESPACIADO Y LEGIBILIDAD ÓPTIMOS */}
      <section id="demo" className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-10 scroll-mt-24">
        <Reveal>
          <div className="mb-8">
            <span className="text-xs font-mono font-bold uppercase tracking-wider text-primary">Sección interactiva</span>
            <h2 className="text-2xl font-bold tracking-tight text-foreground mt-1">05. Controles de la Demo Interactiva</h2>
            <p className="text-sm text-muted-foreground mt-1 max-w-3xl">
              Parámetros interactivos para experimentar y escuchar cómo se transforma la posición, amplitud y movimiento de una fuente en el campo espacial 3D.
            </p>
          </div>

          {/* Grid de 4 controles: balanceado, simétrico, sin sobreposiciones */}
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 sm:gap-6 mb-6">
            {/* Control 1: Dirección */}
            <div className="glass p-5 sm:p-6 rounded-2xl border border-border flex flex-col justify-between h-full min-w-0 hover:border-primary/40 transition-colors">
              <div>
                <div className="flex items-center gap-2.5 mb-3">
                  <div className="p-2 rounded-xl bg-primary/15 text-primary shrink-0">
                    <Compass className="w-4 h-4" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-foreground">Dirección</h3>
                    <span className="text-[10px] font-mono text-primary font-semibold">Azimut (−180° a +180°)</span>
                  </div>
                </div>
                <p className="text-xs text-muted-foreground leading-relaxed mb-4">
                  Ubica la fuente en el plano horizontal alrededor del oyente en 360 grados.
                </p>
              </div>

              <div className="bg-secondary/40 p-3 rounded-xl border border-border/60 text-[11px] font-mono space-y-1.5 mt-auto">
                <div className="flex justify-between items-center text-muted-foreground">
                  <span>Frente:</span>
                  <span className="font-bold text-foreground">0°</span>
                </div>
                <div className="flex justify-between items-center text-muted-foreground">
                  <span>Izquierda:</span>
                  <span className="font-bold text-foreground">+90°</span>
                </div>
                <div className="flex justify-between items-center text-muted-foreground">
                  <span>Derecha:</span>
                  <span className="font-bold text-foreground">−90°</span>
                </div>
                <div className="flex justify-between items-center text-muted-foreground">
                  <span>Atrás:</span>
                  <span className="font-bold text-foreground">±180°</span>
                </div>
              </div>
            </div>

            {/* Control 2: Altura */}
            <div className="glass p-5 sm:p-6 rounded-2xl border border-border flex flex-col justify-between h-full min-w-0 hover:border-primary/40 transition-colors">
              <div>
                <div className="flex items-center gap-2.5 mb-3">
                  <div className="p-2 rounded-xl bg-primary/15 text-primary shrink-0">
                    <MoveVertical className="w-4 h-4" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-foreground">Altura</h3>
                    <span className="text-[10px] font-mono text-primary font-semibold">Elevación (−90° a +90°)</span>
                  </div>
                </div>
                <p className="text-xs text-muted-foreground leading-relaxed mb-4">
                  Ajusta la posición vertical de la fuente entre el suelo (nadir) y el cenit superior.
                </p>
              </div>

              <div className="bg-secondary/40 p-3 rounded-xl border border-border/60 text-[11px] font-mono space-y-1.5 mt-auto">
                <div className="flex justify-between items-center text-muted-foreground">
                  <span>Cenit (arriba):</span>
                  <span className="font-bold text-foreground">+90°</span>
                </div>
                <div className="flex justify-between items-center text-muted-foreground">
                  <span>Horizontal:</span>
                  <span className="font-bold text-foreground">0°</span>
                </div>
                <div className="flex justify-between items-center text-muted-foreground">
                  <span>Nadir (abajo):</span>
                  <span className="font-bold text-foreground">−90°</span>
                </div>
              </div>
            </div>

            {/* Control 3: Apertura */}
            <div className="glass p-5 sm:p-6 rounded-2xl border border-border flex flex-col justify-between h-full min-w-0 hover:border-primary/40 transition-colors">
              <div>
                <div className="flex items-center gap-2.5 mb-3">
                  <div className="p-2 rounded-xl bg-primary/15 text-primary shrink-0">
                    <Maximize className="w-4 h-4" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-foreground">Apertura</h3>
                    <span className="text-[10px] font-mono text-primary font-semibold">Extensión (0% a 100%)</span>
                  </div>
                </div>
                <p className="text-xs text-muted-foreground leading-relaxed mb-4">
                  Controla la amplitud estéreo percibida modulando la componente lateral <em>Side</em>.
                </p>
              </div>

              <div className="bg-secondary/40 p-3 rounded-xl border border-border/60 text-[11px] font-mono space-y-1.5 mt-auto">
                <div className="flex justify-between items-center text-muted-foreground">
                  <span>0% (Mínimo):</span>
                  <span className="font-bold text-foreground">Puntual</span>
                </div>
                <div className="flex justify-between items-center text-muted-foreground">
                  <span>50% (Medio):</span>
                  <span className="font-bold text-foreground">Estéreo natural</span>
                </div>
                <div className="flex justify-between items-center text-muted-foreground">
                  <span>100% (Máximo):</span>
                  <span className="font-bold text-foreground">Máxima amplitud</span>
                </div>
              </div>
            </div>

            {/* Control 4: Movimiento */}
            <div className="glass p-5 sm:p-6 rounded-2xl border border-primary/30 shadow-md shadow-primary/5 flex flex-col justify-between h-full min-w-0 hover:border-primary transition-colors">
              <div>
                <div className="flex items-center gap-2.5 mb-3">
                  <div className="p-2 rounded-xl bg-primary/20 text-primary shrink-0">
                    <RefreshCw className="w-4 h-4" />
                  </div>
                  <div>
                    <h3 className="text-sm font-bold text-foreground">Movimiento</h3>
                    <span className="text-[10px] font-mono text-primary font-semibold">Órbita 3D (0% a 100%)</span>
                  </div>
                </div>
                <p className="text-xs text-muted-foreground leading-relaxed mb-4">
                  Activa una trayectoria dinámica continua en órbita 3D alrededor de la posición seleccionada.
                </p>
              </div>

              <div className="bg-secondary/40 p-3 rounded-xl border border-border/60 text-[11px] font-mono space-y-1.5 mt-auto">
                <div className="flex justify-between items-center text-muted-foreground">
                  <span>0% (Mínimo):</span>
                  <span className="font-bold text-foreground">Estático (fijo)</span>
                </div>
                <div className="flex justify-between items-center text-muted-foreground">
                  <span>50% (Medio):</span>
                  <span className="font-bold text-foreground">Órbita suave</span>
                </div>
                <div className="flex justify-between items-center text-muted-foreground">
                  <span>100% (Máximo):</span>
                  <span className="font-bold text-foreground">Rotación 3D</span>
                </div>
              </div>
            </div>
          </div>

          {/* Tarjeta Informativa sobre el Límite de 15 Segundos en la Demo */}
          <div className="glass p-5 sm:p-6 rounded-2xl border border-primary/30 flex flex-col sm:flex-row items-start sm:items-center gap-4 bg-secondary/30">
            <div className="p-2.5 rounded-xl bg-primary/20 text-primary shrink-0">
              <Clock className="w-6 h-6" />
            </div>
            <div className="text-xs leading-relaxed text-muted-foreground flex-1">
              <span className="font-bold text-foreground block text-sm mb-0.5">Duración admitida en la Demo interactiva:</span>
              Para ofrecer una respuesta ágil e interactiva en tiempo real al mover los controles, la Demo procesa un fragmento de <strong>hasta 15 segundos</strong> del archivo de audio cargado. Para procesar pistas musicales completas sin restricción de tiempo, utiliza la sección principal <strong>Conversor</strong>.
            </div>
          </div>
        </Reveal>
      </section>

      {/* 7. REGISTRO, INICIO DE SESIÓN Y MIS CONVERSIONES */}
      <section id="conversiones" className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-10 scroll-mt-24">
        <Reveal>
          <div className="mb-8">
            <h2 className="text-2xl font-bold tracking-tight text-foreground">06. Cuentas y «Mis Conversiones»</h2>
            <p className="text-sm text-muted-foreground mt-1">
              Gestión de usuario e historial para acceder a tus trabajos anteriores.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="glass p-6 sm:p-7 rounded-3xl border border-border flex flex-col justify-between">
              <div>
                <div className="flex items-center gap-3 mb-3">
                  <div className="p-2.5 rounded-xl bg-secondary text-primary">
                    <UserCheck className="w-5 h-5" />
                  </div>
                  <h3 className="text-base font-bold text-foreground">Cuenta de Usuario</h3>
                </div>
                <p className="text-sm text-muted-foreground leading-relaxed mb-3">
                  Puedes registrarte de forma gratuita e iniciar sesión con correo electrónico y contraseña.
                </p>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  El conversor puede utilizarse libremente sin cuenta; sin embargo, al iniciar sesión, cada trabajo se vincula a tu perfil para que puedas consultarlo y re-descargarlo posteriormente.
                </p>
              </div>
            </div>

            <div className="glass p-6 sm:p-7 rounded-3xl border border-primary/30 shadow-md shadow-primary/5 flex flex-col justify-between">
              <div>
                <div className="flex items-center gap-3 mb-3">
                  <div className="p-2.5 rounded-xl bg-primary/20 text-primary">
                    <History className="w-5 h-5" />
                  </div>
                  <h3 className="text-base font-bold text-foreground">Panel «Mis Conversiones»</h3>
                </div>
                <p className="text-sm text-muted-foreground leading-relaxed mb-3">
                  Permite consultar el historial de todas las conversiones asociadas a tu cuenta, visualizando el nombre del archivo, la duración original, la fecha y la frecuencia de muestreo.
                </p>
                <p className="text-sm text-muted-foreground leading-relaxed">
                  Durante el período de almacenamiento temporal (24 horas), puedes descargar directamente los archivos Binaural (WAV/MP3), Binaural 3D (WAV/MP3) y el archivo ambisónico FOA (WAV de 4 canales).
                </p>
              </div>
            </div>
          </div>
        </Reveal>
      </section>

      {/* 8. GLOSARIO DE SIGLAS Y TÉRMINOS TÉCNICOS */}
      <section id="acronimos" className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-10 scroll-mt-24">
        <Reveal>
          <div className="glass p-6 sm:p-8 rounded-3xl border border-border">
            <h2 className="text-xl font-bold text-foreground mb-2">07. Glosario de Siglas y Términos</h2>
            <p className="text-xs text-muted-foreground mb-6">
              Definición de las siglas y términos técnicos utilizados en la plataforma.
            </p>

            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 text-xs">
              <div className="p-3.5 rounded-xl bg-secondary/30 border border-border">
                <span className="font-bold text-primary font-mono block">FOA</span>
                <span className="text-muted-foreground"><em>First-Order Ambisonics</em>. Ambisónicos de primer orden con 4 componentes esféricas (W, Y, Z, X).</span>
              </div>

              <div className="p-3.5 rounded-xl bg-secondary/30 border border-border">
                <span className="font-bold text-primary font-mono block">AmbiX</span>
                <span className="text-muted-foreground">Estándar internacional de intercambio ambisónico adoptado por la industria (ACN/SN3D).</span>
              </div>

              <div className="p-3.5 rounded-xl bg-secondary/30 border border-border">
                <span className="font-bold text-primary font-mono block">ACN</span>
                <span className="text-muted-foreground"><em>Ambisonic Channel Number</em>. Ordenamiento numérico canónico de canales: W=0, Y=1, Z=2, X=3.</span>
              </div>

              <div className="p-3.5 rounded-xl bg-secondary/30 border border-border">
                <span className="font-bold text-primary font-mono block">SN3D</span>
                <span className="text-muted-foreground">Normalización semi-normalizada de Schmidt empleada para ponderar las funciones esféricas.</span>
              </div>

              <div className="p-3.5 rounded-xl bg-secondary/30 border border-border">
                <span className="font-bold text-primary font-mono block">SAD</span>
                <span className="text-muted-foreground"><em>Sampling Ambisonic Decoder</em>. Decodificador analítico óptimo formulado por Zotter y Frank.</span>
              </div>

              <div className="p-3.5 rounded-xl bg-secondary/30 border border-border">
                <span className="font-bold text-primary font-mono block">HRIR / HRTF</span>
                <span className="text-muted-foreground"><em>Head-Related Impulse Response / Transfer Function</em>. Filtros acústicos que modelan la anatomía de la cabeza.</span>
              </div>

              <div className="p-3.5 rounded-xl bg-secondary/30 border border-border">
                <span className="font-bold text-primary font-mono block">SADIE II (D1)</span>
                <span className="text-muted-foreground">Base de datos de HRIR de alta resolución medida por la Universidad de York (sujeto D1).</span>
              </div>

              <div className="p-3.5 rounded-xl bg-secondary/30 border border-border">
                <span className="font-bold text-primary font-mono block">MSC</span>
                <span className="text-muted-foreground"><em>Magnitude Squared Coherence</em>. Coherencia espectral temporal que discrimina componentes directas de difusas.</span>
              </div>

              <div className="p-3.5 rounded-xl bg-secondary/30 border border-border">
                <span className="font-bold text-primary font-mono block">FLU, FRD, BLD, BRU</span>
                <span className="text-muted-foreground">Cápsulas tetraédricas: Front-Left-Up, Front-Right-Down, Back-Left-Down, Back-Right-Up.</span>
              </div>
            </div>
          </div>
        </Reveal>
      </section>

      {/* 9. RECOMENDACIONES DE ESCUCHA */}
      <section id="escucha" className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 py-10 mb-8 scroll-mt-24">
        <Reveal>
          <div className="glass p-6 sm:p-10 rounded-[2.5rem] border border-border text-center">
            <h2 className="text-2xl font-bold tracking-tight mb-8">08. Recomendaciones de Escucha y Uso</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 max-w-3xl mx-auto text-left">
              <div className="p-5 rounded-2xl bg-secondary/30 border border-border flex items-start gap-3.5">
                <div className="p-2.5 rounded-xl bg-secondary text-primary shrink-0">
                  <Headphones className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="font-bold text-sm text-foreground mb-1">Uso Indispensable de Audífonos</h4>
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    Para percibir con fidelidad las diferencias de tiempo e intensidad generadas por las HRIR, se recomienda utilizar audífonos estéreo de diadema o intraaurales, evitando altavoces externos que mezclen las señales antes de llegar a los oídos.
                  </p>
                </div>
              </div>

              <div className="p-5 rounded-2xl bg-secondary/30 border border-primary/30 flex items-start gap-3.5">
                <div className="p-2.5 rounded-xl bg-primary/20 text-primary shrink-0">
                  <CheckCircle2 className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="font-bold text-sm text-foreground mb-1">Comparación Directa A/B</h4>
                  <p className="text-xs text-muted-foreground leading-relaxed">
                    Utiliza los controles del reproductor web para alternar entre el audio original, la versión binaural estándar y la versión 3D perceptual, apreciando la amplitud del campo y la naturalidad del timbre espacializado.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </Reveal>
      </section>
    </div>
  )
}
