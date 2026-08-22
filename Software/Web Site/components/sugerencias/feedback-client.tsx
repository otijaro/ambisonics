'use client'

import { useState } from 'react'
import { Send, CheckCircle2, AlertCircle, MessageSquareHeart } from 'lucide-react'
import { Reveal } from '@/components/reveal'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Button } from '@/components/ui/button'
import { sendFeedback } from '@/lib/api'

type Status = 'idle' | 'sending' | 'ok' | 'error'

export function FeedbackClient() {
  const [nombre, setNombre] = useState('')
  const [correo, setCorreo] = useState('')
  const [mensaje, setMensaje] = useState('')
  const [status, setStatus] = useState<Status>('idle')
  const [error, setError] = useState('')

  const valid = nombre.trim() && /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(correo) && mensaje.trim().length >= 5

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!valid || status === 'sending') return
    setStatus('sending')
    setError('')
    try {
      await sendFeedback({ nombre: nombre.trim(), correo: correo.trim(), mensaje: mensaje.trim() })
      setStatus('ok')
      setNombre('')
      setCorreo('')
      setMensaje('')
    } catch (err) {
      setStatus('error')
      setError(err instanceof Error ? err.message : 'No se pudo enviar tu mensaje.')
    }
  }

  return (
    <div className="mx-auto max-w-2xl">
      <Reveal>
        <Card className="glow-border relative overflow-hidden border-border/60 bg-card/60 p-6 backdrop-blur-sm sm:p-8">
          <div className="mb-6 flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-xl border border-primary/30 bg-primary/10 text-primary">
              <MessageSquareHeart className="h-5 w-5" />
            </div>
            <div>
              <h2 className="text-lg font-semibold">Cuéntanos tu idea</h2>
              <p className="text-sm text-muted-foreground">Leemos cada mensaje. Gracias por ayudarnos a mejorar.</p>
            </div>
          </div>

          {status === 'ok' ? (
            <div className="flex flex-col items-center gap-3 rounded-xl border border-primary/30 bg-primary/5 px-6 py-10 text-center">
              <CheckCircle2 className="h-10 w-10 text-primary" />
              <p className="text-base font-medium">¡Mensaje enviado!</p>
              <p className="text-sm text-muted-foreground">
                Gracias por tu sugerencia. La tendremos en cuenta para las próximas versiones.
              </p>
              <Button
                variant="secondary"
                className="mt-2 border border-border bg-secondary text-secondary-foreground hover:bg-accent"
                onClick={() => setStatus('idle')}
              >
                Enviar otra
              </Button>
            </div>
          ) : (
            <form onSubmit={onSubmit} className="flex flex-col gap-5">
              <div className="flex flex-col gap-2">
                <Label htmlFor="nombre">Nombre</Label>
                <Input
                  id="nombre"
                  value={nombre}
                  onChange={(e) => setNombre(e.target.value)}
                  placeholder="Tu nombre"
                  autoComplete="name"
                />
              </div>
              <div className="flex flex-col gap-2">
                <Label htmlFor="correo">Correo</Label>
                <Input
                  id="correo"
                  type="email"
                  value={correo}
                  onChange={(e) => setCorreo(e.target.value)}
                  placeholder="tu@correo.com"
                  autoComplete="email"
                />
              </div>
              <div className="flex flex-col gap-2">
                <Label htmlFor="mensaje">Mensaje</Label>
                <Textarea
                  id="mensaje"
                  value={mensaje}
                  onChange={(e) => setMensaje(e.target.value)}
                  placeholder="Comparte tu sugerencia, idea o reporte de error…"
                  rows={5}
                />
              </div>

              {status === 'error' && (
                <div className="flex items-center gap-2 rounded-lg border border-destructive/40 bg-destructive/10 px-3 py-2 text-sm text-destructive">
                  <AlertCircle className="h-4 w-4 shrink-0" />
                  {error}
                </div>
              )}

              <Button
                type="submit"
                disabled={!valid || status === 'sending'}
                className="bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
              >
                {status === 'sending' ? 'Enviando…' : 'Enviar sugerencia'}
                <Send className="ml-1 h-4 w-4" />
              </Button>
            </form>
          )}
        </Card>
      </Reveal>
    </div>
  )
}
