'use client'

import { useRef, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { Loader2, Sparkles, Info, AlertCircle, HelpCircle } from 'lucide-react'
import { FileDropzone } from '@/components/file-dropzone'
import { AudioResult } from '@/components/audio-result'
import { Progress } from '@/components/ui/progress'
import { buttonVariants } from '@/components/ui/button'
import { convertAudio, type ConvertResponse, type ConversionOutput } from '@/lib/api'
import { cn } from '@/lib/utils'

type Status = 'idle' | 'processing' | 'done' | 'error'

// Formatos expuestos al usuario (output_foa.wav nunca se muestra).
const FORMAT_META: Record<string, { title: string; description: string; hasMp3: boolean; group: string }> = {
  binaural: { title: 'Binaural', description: 'Escucha con audífonos, sonido envolvente.', hasMp3: true, group: 'Binaural' },
  binaural_3d: { title: 'Binaural 3D perceptual', description: 'Percepción espacial mejorada con altura.', hasMp3: true, group: 'Binaural' },
}

const GROUPS = ['Binaural']

export function ConversorClient() {
  const [file, setFile] = useState<File | null>(null)
  const [conversionMode, setConversionMode] = useState<'stereo' | 'tetra_4mic'>('stereo')
  const [status, setStatus] = useState<Status>('idle')
  const [progress, setProgress] = useState(0)
  const [outputs, setOutputs] = useState<ConversionOutput[]>([])
  const [error, setError] = useState<string | null>(null)
  const [performance, setPerformance] = useState<{ processingTime: number; originalDuration: number } | null>(null)
  const timerRef = useRef<ReturnType<typeof setInterval> | null>(null)

  const startFakeProgress = () => {
    setProgress(8)
    timerRef.current = setInterval(() => {
      setProgress((p) => (p >= 92 ? p : p + Math.random() * 6))
    }, 500)
  }
  const stopFakeProgress = () => {
    if (timerRef.current) clearInterval(timerRef.current)
    timerRef.current = null
  }

  const handleProcess = async () => {
    if (!file) return
    setStatus('processing')
    setError(null)
    setOutputs([])
    startFakeProgress()
    try {
      const res: ConvertResponse = await convertAudio(file, conversionMode)
      stopFakeProgress()
      setProgress(100)
      setOutputs(res.outputs.filter((o) => o.key in FORMAT_META))
      if (res.processing_seconds != null && res.original_duration_seconds != null) {
        setPerformance({ processingTime: res.processing_seconds, originalDuration: res.original_duration_seconds })
      } else {
        setPerformance(null)
      }
      setStatus('done')
    } catch (e) {
      stopFakeProgress()
      setError(e instanceof Error ? e.message : 'Ocurrió un error inesperado.')
      setStatus('error')
    }
  }

  const grouped = GROUPS.map((g) => ({
    group: g,
    items: outputs.filter((o) => FORMAT_META[o.key]?.group === g),
  })).filter((g) => g.items.length > 0)

  return (
    <div className="grid gap-8 lg:grid-cols-2">
      {/* Columna izquierda: subida */}
      <div className="space-y-6">
        <div className="rounded-3xl glass p-6 sm:p-8">
          <h2 className="text-lg font-semibold text-foreground">Sube tu archivo</h2>
          <p className="mt-1 text-sm text-muted-foreground">
            Sube tu archivo estéreo o de 4 canales. Nosotros nos encargamos del resto.
          </p>

          <div className="mt-6">
            <FileDropzone file={file} onFileChange={setFile} disabled={status === 'processing'} />
          </div>

          <div className="mt-6 space-y-3">
            <label className="text-sm font-medium text-foreground">Modo de micrófono / Entrada</label>
            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <button
                type="button"
                onClick={() => setConversionMode('stereo')}
                disabled={status === 'processing'}
                className={cn(
                  "flex flex-col items-start rounded-2xl border p-4 text-left transition-all duration-200 cursor-pointer disabled:opacity-50",
                  conversionMode === 'stereo'
                    ? "border-primary bg-primary/10 ring-1 ring-primary"
                    : "border-border bg-secondary/35 hover:bg-secondary/60"
                )}
              >
                <span className="text-sm font-semibold text-foreground">Opción 1: Estéreo</span>
                <span className="mt-1 text-xs text-muted-foreground">
                  Para audios estándar de 2 canales (L/R). Estimación espacial 3D.
                </span>
              </button>

              <button
                type="button"
                onClick={() => setConversionMode('tetra_4mic')}
                disabled={status === 'processing'}
                className={cn(
                  "flex flex-col items-start rounded-2xl border p-4 text-left transition-all duration-200 cursor-pointer disabled:opacity-50",
                  conversionMode === 'tetra_4mic'
                    ? "border-primary bg-primary/10 ring-1 ring-primary"
                    : "border-border bg-secondary/35 hover:bg-secondary/60"
                )}
              >
                <span className="text-sm font-semibold text-foreground">Opción 2: 4 Micrófonos</span>
                <span className="mt-1 text-xs text-muted-foreground">
                  Para audios de 4 canales (FLU, FRD, BLD, BRU) en formato A.
                </span>
              </button>
            </div>
          </div>

          <AnimatePresence>
            {conversionMode === 'tetra_4mic' && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-6 overflow-hidden rounded-2xl border border-border bg-secondary/30 p-4"
              >
                <h3 className="mb-3 text-sm font-semibold text-foreground">¿Cómo funciona la captura con 4 micrófonos?</h3>
                <p className="mb-4 text-xs text-muted-foreground">
                  Captura una escena sonora con 4 canales simultáneos (FLU, FRD, BLD, BRU) y conviértela a formato ambisónico para una escucha espacial realista.
                </p>
                <video 
                  src="/opcion2.mp4" 
                  controls 
                  playsInline
                  className="w-full rounded-xl border border-border shadow-sm"
                />
              </motion.div>
            )}
          </AnimatePresence>

          <button
            onClick={handleProcess}
            disabled={!file || status === 'processing'}
            className={cn(
              buttonVariants({ variant: 'default' }),
              'mt-6 h-12 w-full bg-primary text-base text-primary-foreground hover:bg-primary/90 glow-purple disabled:opacity-40',
            )}
          >
            {status === 'processing' ? (
              <>
                <Loader2 className="mr-1 h-4 w-4 animate-spin" /> Convirtiendo audio…
              </>
            ) : (
              <>
                <Sparkles className="mr-1 h-4 w-4" /> Procesar audio
              </>
            )}
          </button>

          <AnimatePresence>
            {status === 'processing' && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                className="mt-5 overflow-hidden"
              >
                <Progress value={progress} className="h-2" />
                <p className="mt-3 text-center text-sm text-muted-foreground">
                  Convirtiendo audio… No cierres la ventana.
                </p>
              </motion.div>
            )}
          </AnimatePresence>

          {status === 'error' && error && (
            <div className="mt-5 flex items-start gap-3 rounded-xl border border-destructive/30 bg-destructive/10 p-4 text-sm text-destructive">
              <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
              <p>{error}</p>
            </div>
          )}
        </div>

        {/* Tarjeta informativa */}
        <div className="rounded-3xl glass p-6 sm:p-8">
          <div className="flex items-center gap-2">
            <HelpCircle className="h-5 w-5 text-primary" />
            <h3 className="font-semibold text-foreground">¿Cuál formato debo descargar?</h3>
          </div>
          <div className="mt-5 grid gap-4 sm:grid-cols-2">
            <div className="rounded-2xl border border-border bg-secondary/50 p-4">
              <p className="text-sm font-semibold text-foreground">WAV</p>
              <p className="mt-1 text-sm text-muted-foreground">
                Mayor calidad. Ideal para VLC y computadores.
              </p>
            </div>
            <div className="rounded-2xl border border-border bg-secondary/50 p-4">
              <p className="text-sm font-semibold text-foreground">MP3</p>
              <p className="mt-1 text-sm text-muted-foreground">
                Mayor compatibilidad. Ideal para teléfonos móviles y WhatsApp.
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Columna derecha: resultados */}
      <div className="rounded-3xl glass p-6 sm:p-8">
        <h2 className="text-lg font-semibold text-foreground">Resultados</h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Tus formatos espaciales aparecerán aquí, organizados por categoría.
        </p>

        {status !== 'done' && (
          <div className="mt-10 flex flex-col items-center justify-center rounded-2xl border border-dashed border-border py-16 text-center">
            <span className="flex h-14 w-14 items-center justify-center rounded-2xl bg-accent text-primary">
              <Info className="h-6 w-6" />
            </span>
            <p className="mt-4 max-w-xs text-sm text-muted-foreground">
              Sube un archivo y presiona <span className="text-foreground">Procesar audio</span> para
              generar tus versiones espaciales.
            </p>
          </div>
        )}

        {status === 'done' && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-6 space-y-8"
          >
            {performance && (
              <div className="rounded-2xl border border-primary/30 bg-secondary/20 p-5">
                <h3 className="mb-4 text-sm font-semibold text-foreground">Rendimiento del procesamiento</h3>
                <div className="grid grid-cols-1 gap-3 sm:grid-cols-3 text-center sm:text-left">
                  <div className="rounded-xl bg-background/50 p-3">
                    <p className="text-lg font-semibold text-primary">{performance.originalDuration.toFixed(1)} s</p>
                    <p className="text-xs text-muted-foreground mt-1">Duración</p>
                  </div>
                  <div className="rounded-xl bg-background/50 p-3">
                    <p className="text-lg font-semibold text-primary">{performance.processingTime.toFixed(2)} s</p>
                    <p className="text-xs text-muted-foreground mt-1">Procesamiento</p>
                  </div>
                  <div className="rounded-xl bg-background/50 p-3">
                    <p className="text-lg font-semibold text-primary">{((performance.processingTime / performance.originalDuration) * 100).toFixed(1)} %</p>
                    <p className="text-xs text-muted-foreground mt-1">Tiempo relativo</p>
                  </div>
                </div>
              </div>
            )}
            
            {grouped.map((section) => (
              <div key={section.group}>
                <h3 className="mb-3 text-sm font-semibold uppercase tracking-wide text-muted-foreground">
                  {section.group}
                </h3>
                <div className="space-y-4">
                  {section.items.map((o) => {
                    const meta = FORMAT_META[o.key]
                    return (
                      <AudioResult
                        key={o.key}
                        title={meta.title}
                        description={meta.description}
                        wavUrl={o.wavUrl}
                        mp3Url={meta.hasMp3 ? o.mp3Url : undefined}
                      />
                    )
                  })}
                </div>
              </div>
            ))}
          </motion.div>
        )}
      </div>
    </div>
  )
}
