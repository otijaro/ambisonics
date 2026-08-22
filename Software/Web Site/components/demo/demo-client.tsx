'use client'

import { useState, useEffect, useRef } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { Compass, MoveVertical, Maximize, RefreshCw, Loader2, Play, AlertCircle, Info } from 'lucide-react'
import { Slider } from '@/components/ui/slider'
import { Switch } from '@/components/ui/switch'
import { Label } from '@/components/ui/label'
import { buttonVariants } from '@/components/ui/button'
import { FileDropzone } from '@/components/file-dropzone'
import { AudioResult } from '@/components/audio-result'
import { SpatialSphere } from '@/components/demo/spatial-sphere'
import { runDemo, type DemoResponse } from '@/lib/api'
import { cn } from '@/lib/utils'
import dynamic from 'next/dynamic'

const Visualizer3D = dynamic(() => import('@/components/demo/visualizer-3d').then(m => m.Visualizer3D), { ssr: false })

type Status = 'idle' | 'processing' | 'done' | 'error'

export function DemoClient() {
  const [showDemo, setShowDemo] = useState(false)
  const [demoControls, setDemoControls] = useState({
    direccion: 0,
    altura: 20,
    apertura: 45,
    movimiento: 35,
  })

  const [status, setStatus] = useState<Status>('idle')
  const [result, setResult] = useState<DemoResponse | null>(null)
  const [file, setFile] = useState<File | null>(null)
  const [error, setError] = useState<string | null>(null)

  const [lastProcessed, setLastProcessed] = useState<typeof demoControls | null>(null)

  const requestSeq = useRef(0)
  const [debouncedControls, setDebouncedControls] = useState(demoControls)

  // 1. Debounce de los controles
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedControls(demoControls)
    }, 700)
    return () => clearTimeout(handler)
  }, [demoControls])

  // 2. Procesamiento automático cuando cambia el debounced o el archivo
  useEffect(() => {
    if (!file) return

    let isActive = true
    const seq = ++requestSeq.current

    const process = async () => {
      setStatus('processing')
      setError(null)
      // setResult(null) // No borramos el anterior para evitar parpadeos y conservar la previsualización antigua hasta que la nueva esté lista
      try {
        const direccion = Number.isFinite(Number(debouncedControls.direccion)) ? Number(debouncedControls.direccion) : 0
        const altura = Number.isFinite(Number(debouncedControls.altura)) ? Number(debouncedControls.altura) : 25
        const apertura = Number.isFinite(Number(debouncedControls.apertura)) ? Number(debouncedControls.apertura) : 50
        const movimiento = Number.isFinite(Number(debouncedControls.movimiento)) ? Number(debouncedControls.movimiento) : 40

        const res = await runDemo(file, { direccion, altura, apertura, movimiento })
        if (isActive && seq === requestSeq.current) {
          setResult(res)
          setLastProcessed({ direccion, altura, apertura, movimiento })
          setStatus('done')
        }
      } catch (e) {
        if (isActive && seq === requestSeq.current) {
          setError(e instanceof Error ? e.message : 'Ocurrió un error inesperado.')
          setStatus('error')
        }
      }
    }

    process()

    return () => {
      isActive = false
    }
  }, [debouncedControls, file])

  if (!showDemo) {
    return (
      <div className="flex flex-col items-center justify-center text-center max-w-6xl mx-auto w-full px-4 animate-in fade-in zoom-in-95 duration-500">
        <span className="inline-flex items-center gap-2 rounded-full border border-border bg-secondary/60 px-3 py-1 text-xs text-muted-foreground uppercase tracking-widest font-semibold mb-6">
          DEMO INTERACTIVA
        </span>
        <h1 className="text-balance text-4xl font-semibold tracking-tight sm:text-5xl mb-4">
          Explora el sonido en el espacio
        </h1>
        <p className="text-pretty text-base sm:text-lg text-muted-foreground leading-relaxed max-w-2xl mb-10">
          Ajusta los parámetros espaciales y observa cómo cambia la representación del campo sonoro antes de realizar una conversión.
        </p>
        
        <div className="w-full max-w-4xl mx-auto mb-10">
          <img 
            src="/demo-referencia.png" 
            alt="Montaje tetraédrico de referencia"
            className="w-full h-auto object-contain rounded-2xl border border-border bg-secondary shadow-lg"
          />
        </div>
        
        <button 
          onClick={() => setShowDemo(true)}
          className="inline-flex h-14 items-center justify-center rounded-2xl bg-primary px-10 text-base font-bold text-primary-foreground hover:bg-primary/90 transition-all shadow-lg shadow-primary/25 hover:shadow-primary/40 hover:-translate-y-0.5 active:translate-y-0 mb-8"
        >
          Probar Demo interactiva
        </button>
      </div>
    )
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8 animate-in fade-in duration-500">
      <div className="max-w-2xl mb-12">
        <span className="inline-flex items-center gap-2 rounded-full border border-border bg-secondary/60 px-3 py-1 text-xs text-muted-foreground uppercase font-semibold tracking-widest">
          DEMO INTERACTIVA
        </span>
        <h1 className="mt-5 text-balance text-4xl font-semibold tracking-tight sm:text-5xl">
          Explora el sonido en el espacio
        </h1>
        <p className="mt-4 text-pretty text-lg leading-relaxed text-muted-foreground">
          Ajusta los parámetros para explorar cómo cambia la posición y el movimiento del sonido en el
          espacio ambisónico.
        </p>
      </div>

      {/* Fila Superior: Audio de entrada y Cuadro explicativo */}
      <div className="grid gap-8 lg:grid-cols-2 items-stretch">
        <div className="rounded-3xl glass p-6 sm:p-8 h-full">
          <h2 className="text-lg font-semibold text-foreground">Audio de entrada</h2>
          <p className="mt-1 text-sm text-muted-foreground">Sube una pista para escuchar el efecto espacial.</p>
          <div className="mt-6">
            <FileDropzone file={file} onFileChange={setFile} disabled={status === 'processing'} />
          </div>
        </div>

        <div className="rounded-3xl glass p-6 sm:p-8 h-full flex flex-col justify-center border border-primary/20">
          <span className="inline-block text-[10px] font-bold tracking-widest uppercase text-primary mb-2">
            GUÍA RÁPIDA
          </span>
          <h2 className="text-lg font-semibold text-foreground mb-3">Controla y observa el campo sonoro</h2>
          <p className="text-sm leading-relaxed text-muted-foreground mb-6">
            Carga una señal de audio y modifica los parámetros espaciales para observar en tiempo real cómo cambia la posición y extensión de la fuente dentro del campo ambisónico.
          </p>
          <div className="grid grid-cols-2 gap-4 mb-6">
            <div className="flex items-center gap-3">
              <div className="p-2 bg-secondary/80 rounded-lg text-primary"><Compass className="w-4 h-4" /></div>
              <div>
                <p className="text-xs font-bold text-foreground">Dirección</p>
                <p className="text-[10px] text-muted-foreground">posición horizontal</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="p-2 bg-secondary/80 rounded-lg text-primary"><MoveVertical className="w-4 h-4" /></div>
              <div>
                <p className="text-xs font-bold text-foreground">Altura</p>
                <p className="text-[10px] text-muted-foreground">componente vertical</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="p-2 bg-secondary/80 rounded-lg text-primary"><Maximize className="w-4 h-4" /></div>
              <div>
                <p className="text-xs font-bold text-foreground">Apertura</p>
                <p className="text-[10px] text-muted-foreground">extensión espacial</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <div className="p-2 bg-secondary/80 rounded-lg text-primary"><RefreshCw className="w-4 h-4" /></div>
              <div>
                <p className="text-xs font-bold text-foreground">Movimiento</p>
                <p className="text-[10px] text-muted-foreground">variación dinámica</p>
              </div>
            </div>
          </div>
          <div className="p-3 bg-primary/5 border border-primary/20 rounded-xl">
            <p className="text-[11px] text-primary font-medium text-center">
              Los controles y la visualización 3D responden de forma conjunta.
            </p>
          </div>
        </div>
      </div>

      {/* Fila Inferior: Controles y Visualizador */}
      <div className="grid gap-8 lg:grid-cols-2 items-start">
        {/* Izquierda: controles */}
        <div className="rounded-3xl glass p-6 sm:p-8">

          <h2 className="text-lg font-semibold text-foreground">Controles espaciales</h2>

          <div className="mt-6 space-y-8">
            {/* Dirección */}
            <ControlBlock
              icon={Compass}
              label="Dirección"
              value={`${demoControls.direccion}°`}
              description="Controla desde dónde proviene el sonido alrededor del oyente."
            >
              <input
                type="range"
                min="-90"
                max="90"
                step="1"
                className="w-full"
                value={demoControls.direccion}
                onChange={(e) =>
                  setDemoControls((prev) => ({
                    ...prev,
                    direccion: Number(e.target.value),
                  }))
                }
              />
            </ControlBlock>

            {/* Altura */}
            <ControlBlock
              icon={MoveVertical}
              label="Altura"
              value={`${demoControls.altura}°`}
              description="Controla si el sonido proviene desde abajo, al nivel del oyente o desde arriba."
            >
              <input
                type="range"
                min="0"
                max="100"
                step="1"
                className="w-full"
                value={demoControls.altura}
                onChange={(e) =>
                  setDemoControls((prev) => ({
                    ...prev,
                    altura: Number(e.target.value),
                  }))
                }
              />
            </ControlBlock>

            {/* Apertura */}
            <ControlBlock
              icon={Maximize}
              label="Apertura"
              value={`${demoControls.apertura}%`}
              description="Modifica la amplitud espacial del sonido."
            >
              <input
                type="range"
                min="0"
                max="100"
                step="1"
                className="w-full"
                value={demoControls.apertura}
                onChange={(e) =>
                  setDemoControls((prev) => ({
                    ...prev,
                    apertura: Number(e.target.value),
                  }))
                }
              />
            </ControlBlock>

            {/* Movimiento */}
            <div className="flex items-start gap-4">
              <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-accent text-primary">
                <RefreshCw className="h-5 w-5" />
              </span>
              <div className="flex-1">
                <div className="flex flex-col gap-3">
                  <div className="flex items-center justify-between">
                    <Label htmlFor="movimiento" className="text-sm font-medium text-foreground">
                      Movimiento
                    </Label>
                    <span className="font-mono text-sm text-primary">{demoControls.movimiento}</span>
                  </div>
                  <input
                    id="movimiento"
                    type="range"
                    min="0"
                    max="100"
                    step="1"
                    className="w-full"
                    value={demoControls.movimiento}
                    onChange={(e) =>
                      setDemoControls((prev) => ({
                        ...prev,
                        movimiento: Number(e.target.value),
                      }))
                    }
                  />
                </div>
                <p className="mt-1.5 text-xs text-muted-foreground">
                  Hace que el sonido se desplace automáticamente alrededor del oyente.
                </p>
              </div>
            </div>
          </div>

          <div className="mt-8 flex h-12 w-full items-center justify-center rounded-xl bg-secondary/50 text-base font-medium text-foreground border border-border">
            {status === 'processing' ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" /> Actualizando previsualización…
              </>
            ) : status === 'done' ? (
              <>
                <RefreshCw className="mr-2 h-4 w-4" /> Previsualización actualizada
              </>
            ) : (
              'Sube un archivo para comenzar'
            )}
          </div>

          {status === 'error' && error && (
            <div className="mt-5 flex items-start gap-3 rounded-xl border border-destructive/30 bg-destructive/10 p-4 text-sm text-destructive">
              <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
              <p>{error}</p>
            </div>
          )}
        </div>

        {/* Derecha: visualización + resultados */}
        <div className="space-y-6">
        <div className="rounded-3xl glass p-6 sm:p-8">
          <div className="flex items-center justify-between">
            <h2 className="text-lg font-semibold text-foreground">Campo sonoro ambisónico</h2>
          </div>
          <p className="mt-1 text-sm text-muted-foreground">
            Vista frontal: como si tú fueras el oyente en el centro.
          </p>
          <div className="mt-6 flex justify-center w-full">
            <Visualizer3D 
              mode="interactive" 
              direccion={demoControls.direccion} 
              altura={demoControls.altura} 
              apertura={demoControls.apertura} 
              movimiento={demoControls.movimiento} 
            />
          </div>
          <div className="mt-4 grid grid-cols-3 gap-3 text-center">
            <Stat label="Dirección" value={`${demoControls.direccion}°`} />
            <Stat label="Altura" value={`${demoControls.altura}°`} />
            <Stat label="Apertura" value={`${demoControls.apertura}%`} />
          </div>
        </div>

        <div className="rounded-3xl glass p-6 sm:p-8">
          <h2 className="text-lg font-semibold text-foreground">Previsualización</h2>
          {status !== 'done' ? (
            <div className="mt-6 flex flex-col items-center justify-center rounded-2xl border border-dashed border-border py-12 text-center">
              <span className="flex h-12 w-12 items-center justify-center rounded-2xl bg-accent text-primary">
                <Info className="h-5 w-5" />
              </span>
              <p className="mt-3 max-w-xs text-sm text-muted-foreground">
                Ajusta los parámetros y presiona <span className="text-foreground">Actualizar demo</span>.
              </p>
            </div>
          ) : (
            <AnimatePresence>
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="mt-6 space-y-4">
                <AudioResult
                  title="Preview binaural"
                  description="Escucha con audífonos."
                  wavUrl={result?.binaural?.wavUrl}
                  mp3Url={result?.binaural?.mp3Url}
                />
                <AudioResult
                  title="Preview 3D perceptual"
                  description="Percepción espacial con altura."
                  wavUrl={result?.binaural_3d?.wavUrl}
                  mp3Url={result?.binaural_3d?.mp3Url}
                />
                {lastProcessed && (
                  <div className="mt-4 rounded-xl border border-border bg-secondary/50 p-4 font-mono text-xs text-muted-foreground">
                    <p className="mb-2 font-semibold text-foreground">Diagnóstico de últimos parámetros procesados:</p>
                    <ul className="space-y-1">
                      <li>Dirección: {lastProcessed.direccion}</li>
                      <li>Altura: {lastProcessed.altura}</li>
                      <li>Apertura: {lastProcessed.apertura}</li>
                      <li>Movimiento: {lastProcessed.movimiento}</li>
                    </ul>
                  </div>
                )}
              </motion.div>
            </AnimatePresence>
          )}
        </div>
      </div>
    </div>

    </div>
  )
}

function ControlBlock({
  icon: Icon,
  label,
  value,
  description,
  children,
}: {
  icon: React.ComponentType<{ className?: string }>
  label: string
  value: string
  description: string
  children: React.ReactNode
}) {
  return (
    <div className="flex items-start gap-4">
      <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-accent text-primary">
        <Icon className="h-5 w-5" />
      </span>
      <div className="flex-1">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-foreground">{label}</span>
          <span className="font-mono text-sm text-primary">{value}</span>
        </div>
        <div className="mt-3">{children}</div>
        <p className="mt-2 text-xs text-muted-foreground">{description}</p>
      </div>
    </div>
  )
}

function Stat({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-xl border border-border bg-secondary/50 p-3">
      <p className="font-mono text-base text-foreground">{value}</p>
      <p className="text-xs text-muted-foreground">{label}</p>
    </div>
  )
}
