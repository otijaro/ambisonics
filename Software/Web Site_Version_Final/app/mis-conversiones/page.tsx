'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import { useAuth } from '@/components/auth-provider'
import { getMyConversions, type MyConversion } from '@/lib/api'
import { Loader2, HardDrive, Clock, FileAudio, Download } from 'lucide-react'
import { Badge } from '@/components/ui/badge'
import { buttonVariants } from '@/components/ui/button'
import { cn } from '@/lib/utils'

export default function MisConversionesPage() {
  const { user, isLoading } = useAuth()
  const router = useRouter()
  const [conversions, setConversions] = useState<MyConversion[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!isLoading && !user) {
      router.push('/login')
    }
  }, [user, isLoading, router])

  useEffect(() => {
    if (user) {
      getMyConversions()
        .then(setConversions)
        .catch((err) => setError(err.message))
        .finally(() => setLoading(false))
    }
  }, [user])

  if (isLoading || loading) {
    return (
      <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center p-4">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    )
  }

  if (!user) return null

  const getStatusBadge = (status: string, available: boolean) => {
    if (status === 'completed' && available) return <Badge variant="default" className="bg-green-500 hover:bg-green-600">Disponible</Badge>
    if (status === 'completed' && !available) return <Badge variant="secondary">Expirado</Badge>
    if (status === 'failed') return <Badge variant="destructive">Error</Badge>
    if (status === 'deleted') return <Badge variant="outline">Eliminado</Badge>
    return <Badge variant="outline" className="animate-pulse">Procesando</Badge>
  }

  return (
    <div className="bg-aurora min-h-[calc(100vh-4rem)] pb-24 pt-12">
      <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-semibold tracking-tight">Mis conversiones</h1>
          <p className="mt-2 text-muted-foreground">
            Historial de archivos procesados. Los resultados están disponibles por 24 horas.
          </p>
        </div>

        {error && (
          <div className="rounded-xl border border-red-500/20 bg-red-500/10 p-4 text-red-500 mb-6">
            {error}
          </div>
        )}

        {conversions.length === 0 && !error ? (
          <div className="rounded-2xl glass p-12 text-center">
            <HardDrive className="mx-auto h-12 w-12 text-muted-foreground/50 mb-4" />
            <h3 className="text-lg font-medium">Aún no tienes conversiones</h3>
            <p className="mt-1 text-sm text-muted-foreground">
              Tus archivos procesados aparecerán aquí.
            </p>
          </div>
        ) : (
          <div className="grid gap-4">
            {conversions.map((conv) => (
              <div key={conv.id} className="rounded-2xl glass p-5 flex flex-col md:flex-row gap-4 items-start md:items-center justify-between">
                <div>
                  <div className="flex items-center gap-3 mb-1">
                    <FileAudio className="h-5 w-5 text-primary" />
                    <span className="font-medium text-foreground">{conv.original_filename}</span>
                    {getStatusBadge(conv.status, conv.is_available)}
                  </div>
                  <div className="flex flex-wrap items-center gap-4 text-sm text-muted-foreground mt-2">
                    <span className="flex items-center gap-1">
                      <Clock className="h-4 w-4" />
                      {new Date(conv.requested_at).toLocaleString()}
                    </span>
                    {conv.original_duration_seconds && (
                      <span>Duración: {Math.round(conv.original_duration_seconds)}s</span>
                    )}
                    <span className="capitalize border border-border rounded-md px-2 py-0.5 text-xs">
                      {conv.input_mode === 'stereo' ? 'Estéreo' : '4 Canales'}
                    </span>
                  </div>
                </div>

                {conv.status === 'completed' && conv.is_available && conv.files && conv.files.length > 0 && (
                  <div className="flex flex-col gap-3 mt-4 md:mt-0 w-full md:w-auto">
                    {conv.files.map((file) => {
                      if (file.file_type === 'input') return null
                      const isMp3 = file.file_type.endsWith('_mp3')
                      const formatName = file.file_type.replace('_mp3', '').replace('_', ' ')
                      const label = formatName.charAt(0).toUpperCase() + formatName.slice(1) + (isMp3 ? ' MP3' : ' WAV')
                      const url = `/api/processing-requests/${conv.id}/file/${file.file_type}`
                      return (
                        <div key={file.file_type} className="flex flex-col sm:flex-row sm:items-center gap-2">
                          <span className="text-xs font-medium w-28 truncate">{label}</span>
                          {isMp3 && (
                            <audio controls src={url} className="h-8 w-full sm:w-48" preload="none" />
                          )}
                          <a 
                            href={`${url}?download=true`} 
                            download 
                            className={cn(buttonVariants({ variant: 'outline', size: 'sm' }), "h-8 px-3 ml-auto sm:ml-0")}
                            title={`Descargar ${label}`}
                          >
                            <Download className="h-4 w-4 mr-1 sm:mr-0" />
                            <span className="sm:hidden">Descargar</span>
                          </a>
                        </div>
                      )
                    })}
                  </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
