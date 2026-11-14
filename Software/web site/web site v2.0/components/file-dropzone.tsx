'use client'

import { useRef, useState, type DragEvent } from 'react'
import { UploadCloud, FileAudio, X } from 'lucide-react'
import { buttonVariants } from '@/components/ui/button'
import { cn } from '@/lib/utils'

const ACCEPTED = ['.wav', '.mp3']

function formatSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

interface FileDropzoneProps {
  file: File | null
  onFileChange: (file: File | null) => void
  disabled?: boolean
}

export function FileDropzone({ file, onFileChange, disabled }: FileDropzoneProps) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [dragging, setDragging] = useState(false)
  const [duration, setDuration] = useState<number | null>(null)

  const handleFile = (f: File | null) => {
    setDuration(null)
    onFileChange(f)
    if (f) {
      const audio = document.createElement('audio')
      audio.preload = 'metadata'
      audio.onloadedmetadata = () => setDuration(audio.duration)
      audio.src = URL.createObjectURL(f)
    }
  }

  const onDrop = (e: DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setDragging(false)
    if (disabled) return
    const f = e.dataTransfer.files?.[0]
    if (f) handleFile(f)
  }

  const durationLabel =
    duration != null && Number.isFinite(duration)
      ? `${Math.floor(duration / 60)}:${Math.floor(duration % 60)
          .toString()
          .padStart(2, '0')}`
      : '—'

  return (
    <div>
      <div
        onDragOver={(e) => {
          e.preventDefault()
          if (!disabled) setDragging(true)
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={onDrop}
        className={cn(
          'flex flex-col items-center justify-center rounded-2xl border border-dashed p-8 text-center transition-colors',
          dragging ? 'border-primary bg-primary/5' : 'border-border bg-secondary/40',
          disabled && 'pointer-events-none opacity-60',
        )}
      >
        <span className="flex h-14 w-14 items-center justify-center rounded-2xl bg-accent text-primary">
          <UploadCloud className="h-6 w-6" />
        </span>
        <p className="mt-4 text-sm font-medium text-foreground">Arrastra y suelta tu archivo aquí</p>
        <p className="mt-1 text-xs text-muted-foreground">Formatos aceptados: WAV, MP3</p>

        <button
          type="button"
          onClick={() => inputRef.current?.click()}
          className={cn(buttonVariants({ variant: 'default' }), 'mt-5 h-10 bg-primary px-5 text-primary-foreground hover:bg-primary/90')}
        >
          Seleccionar audio
        </button>
        <input
          ref={inputRef}
          type="file"
          accept={ACCEPTED.join(',')}
          className="hidden"
          onChange={(e) => handleFile(e.target.files?.[0] ?? null)}
        />
      </div>

      {file && (
        <div className="mt-4 flex items-center gap-3 rounded-xl border border-border bg-secondary/60 p-3">
          <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-accent text-primary">
            <FileAudio className="h-5 w-5" />
          </span>
          <div className="min-w-0 flex-1">
            <p className="truncate text-sm font-medium text-foreground">{file.name}</p>
            <p className="text-xs text-muted-foreground">
              {formatSize(file.size)} · {durationLabel}
            </p>
          </div>
          {!disabled && (
            <button
              onClick={() => handleFile(null)}
              aria-label="Quitar archivo"
              className="flex h-8 w-8 items-center justify-center rounded-lg text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>
      )}
    </div>
  )
}
