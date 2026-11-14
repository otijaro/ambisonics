'use client'

import { useEffect, useState } from 'react'
import { checkHealth } from '@/lib/api'
import { cn } from '@/lib/utils'

type Status = 'loading' | 'online' | 'offline'

export function HealthIndicator({ className }: { className?: string }) {
  const [status, setStatus] = useState<Status>('loading')

  useEffect(() => {
    let active = true
    const controller = new AbortController()

    const ping = async () => {
      const ok = await checkHealth(controller.signal)
      if (active) setStatus(ok ? 'online' : 'offline')
    }

    ping()
    const id = setInterval(ping, 20000)
    return () => {
      active = false
      controller.abort()
      clearInterval(id)
    }
  }, [])

  const label =
    status === 'online' ? 'Servidor activo' : status === 'offline' ? 'Servidor inactivo' : 'Conectando…'

  return (
    <div className={cn('flex items-center gap-2 text-xs text-muted-foreground', className)}>
      <span className="relative flex h-2.5 w-2.5">
        {status === 'online' && (
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-60" />
        )}
        <span
          className={cn(
            'relative inline-flex h-2.5 w-2.5 rounded-full',
            status === 'online' && 'bg-emerald-400',
            status === 'offline' && 'bg-red-500',
            status === 'loading' && 'bg-amber-400',
          )}
        />
      </span>
      <span className="hidden sm:inline">{label}</span>
    </div>
  )
}
