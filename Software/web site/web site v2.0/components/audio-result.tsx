'use client'

import { useEffect, useRef, useState } from 'react'
import { Play, Pause, Download, AudioLines } from 'lucide-react'
import { buttonVariants } from '@/components/ui/button'
import { cn } from '@/lib/utils'

const dlClass = cn(
  buttonVariants({ variant: 'secondary', size: 'sm' }),
  'h-8 border border-border bg-secondary px-3 text-secondary-foreground hover:bg-accent',
)

interface AudioResultProps {
  title: string
  description?: string
  wavUrl?: string
  mp3Url?: string
  /** Fuente de reproducción (por defecto usa wav, luego mp3). */
  previewUrl?: string
  className?: string
}

function formatTime(s: number) {
  if (!Number.isFinite(s)) return '0:00'
  const m = Math.floor(s / 60)
  const sec = Math.floor(s % 60)
  return `${m}:${sec.toString().padStart(2, '0')}`
}

export function AudioResult({ title, description, wavUrl, mp3Url, previewUrl, className }: AudioResultProps) {
  const src = previewUrl ?? wavUrl ?? mp3Url
  const audioRef = useRef<HTMLAudioElement>(null)
  const [playing, setPlaying] = useState(false)
  const [current, setCurrent] = useState(0)
  const [duration, setDuration] = useState(0)

  useEffect(() => {
    const el = audioRef.current
    if (!el) return
    const onTime = () => setCurrent(el.currentTime)
    const onMeta = () => setDuration(el.duration)
    const onEnd = () => setPlaying(false)
    el.addEventListener('timeupdate', onTime)
    el.addEventListener('loadedmetadata', onMeta)
    el.addEventListener('durationchange', onMeta)
    el.addEventListener('ended', onEnd)
    return () => {
      el.removeEventListener('timeupdate', onTime)
      el.removeEventListener('loadedmetadata', onMeta)
      el.removeEventListener('durationchange', onMeta)
      el.removeEventListener('ended', onEnd)
    }
  }, [src])

  const toggle = () => {
    const el = audioRef.current
    if (!el) return
    if (playing) {
      el.pause()
      setPlaying(false)
    } else {
      el.play()
      setPlaying(true)
    }
  }

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const el = audioRef.current
    if (!el) return
    const newTime = Number(e.target.value)
    el.currentTime = newTime
    setCurrent(newTime)
  }

  return (
    <div className={cn('rounded-2xl glass p-5', className)}>
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3">
          <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-accent text-primary">
            <AudioLines className="h-5 w-5" />
          </span>
          <div>
            <h4 className="text-sm font-semibold text-foreground">{title}</h4>
            {description && <p className="text-xs text-muted-foreground">{description}</p>}
          </div>
        </div>
      </div>

      {src && <audio ref={audioRef} src={src} preload="metadata" crossOrigin="anonymous" />}

      <div className="mt-4 flex items-center gap-3">
        <button
          onClick={toggle}
          disabled={!src}
          aria-label={playing ? 'Pausar' : 'Reproducir'}
          className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary text-primary-foreground transition-transform hover:scale-105 disabled:opacity-40"
        >
          {playing ? <Pause className="h-4 w-4 fill-current" /> : <Play className="ml-0.5 h-4 w-4 fill-current" />}
        </button>
        <input
          type="range"
          min={0}
          max={duration || 100}
          step={0.01}
          value={current}
          onChange={handleSeek}
          disabled={!src || !duration}
          className="flex-1 accent-primary h-1.5 cursor-pointer rounded-full bg-secondary"
        />
        <span className="w-20 shrink-0 text-right font-mono text-xs text-muted-foreground">
          {formatTime(current)} / {formatTime(duration)}
        </span>
      </div>

      <div className="mt-4 flex flex-wrap gap-2">
        {wavUrl ? (
          <a href={wavUrl} download className={dlClass}>
            <Download className="mr-1 h-3.5 w-3.5" /> Descargar WAV
          </a>
        ) : (
          <span className={cn(dlClass, 'pointer-events-none opacity-40')}>
            <Download className="mr-1 h-3.5 w-3.5" /> Descargar WAV
          </span>
        )}
        {mp3Url !== undefined &&
          (mp3Url ? (
            <a href={mp3Url} download className={dlClass}>
              <Download className="mr-1 h-3.5 w-3.5" /> Descargar MP3
            </a>
          ) : (
            <span className={cn(dlClass, 'pointer-events-none opacity-40')}>
              <Download className="mr-1 h-3.5 w-3.5" /> Descargar MP3
            </span>
          ))}
      </div>
    </div>
  )
}
