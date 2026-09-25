'use client'

import { useState, useEffect } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { Send, CheckCircle2, AlertCircle, MessageSquareHeart, X } from 'lucide-react'
import { useAuth } from '@/components/auth-provider'
import { Reveal } from '@/components/reveal'
import { Card } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Button } from '@/components/ui/button'
import { sendFeedback } from '@/lib/api'

type Status = 'idle' | 'sending' | 'ok' | 'error'

export function FeedbackClient() {
  const { user } = useAuth()
  const [nombre, setNombre] = useState('')
  const [correo, setCorreo] = useState('')
  const [mensaje, setMensaje] = useState('')
  const [consent, setConsent] = useState(false)
  const [showPolicy, setShowPolicy] = useState(false)
  const [status, setStatus] = useState<Status>('idle')
  const [error, setError] = useState('')

  const hasPersonalData = nombre.trim() !== '' || correo.trim() !== ''

  useEffect(() => {
    if (user) {
      setNombre(user.name)
      setCorreo(user.email)
    }
  }, [user])

  useEffect(() => {
    if (!hasPersonalData && consent) {
      setConsent(false)
    }
  }, [hasPersonalData, consent])

  const isMessageValid = mensaje.trim().length >= 5
  const isEmailValid = correo.trim() === '' || /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(correo)
  
  const valid = isMessageValid && isEmailValid && (!hasPersonalData || consent)

  async function handleSubmit() {
    if (!valid || status === 'sending') return
    setStatus('sending')
    setError('')
    try {
      const payloadNombre = consent && nombre.trim() ? nombre.trim() : ''
      const payloadCorreo = consent && correo.trim() ? correo.trim() : ''
      
      await sendFeedback({ 
        nombre: payloadNombre, 
        correo: payloadCorreo, 
        mensaje: mensaje.trim() 
      })
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
                type="button"
                variant="secondary"
                className="mt-2 border border-border bg-secondary text-secondary-foreground hover:bg-accent"
                onClick={() => setStatus('idle')}
              >
                Enviar otra
              </Button>
            </div>
          ) : (
            <div className="flex flex-col gap-5">
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
                <div className="flex justify-between items-center">
                  <Label htmlFor="mensaje">Mensaje</Label>
                  <span className={`text-xs ${isMessageValid ? 'text-muted-foreground' : 'text-muted-foreground/60'}`}>
                    {mensaje.trim().length >= 5 ? (
                      `${mensaje.trim().length} caracteres`
                    ) : (
                      `${mensaje.trim().length}/5 mín`
                    )}
                  </span>
                </div>
                <Textarea
                  id="mensaje"
                  value={mensaje}
                  onChange={(e) => setMensaje(e.target.value)}
                  placeholder="Comparte tu sugerencia, idea o reporte de error…"
                  rows={5}
                />
              </div>

              {hasPersonalData && (
                <div className="flex items-start gap-3 rounded-lg border border-border/50 bg-muted/20 p-4">
                  <div className="flex h-5 items-center">
                    <input
                      id="consent"
                      type="checkbox"
                      checked={consent}
                      onChange={(e) => setConsent(e.target.checked)}
                      className="h-4 w-4 cursor-pointer appearance-none rounded border border-primary/50 bg-transparent checked:border-primary checked:bg-primary hover:border-primary focus:outline-none focus:ring-2 focus:ring-primary/30 focus:ring-offset-1 focus:ring-offset-background relative
                      after:content-[''] after:absolute after:hidden checked:after:block after:left-1/2 after:top-1/2 after:-translate-x-1/2 after:-translate-y-1/2 after:w-1.5 after:h-2.5 after:border-r-2 after:border-b-2 after:border-primary-foreground after:rotate-45 after:-mt-0.5"
                    />
                  </div>
                  <div className="grid gap-1.5 leading-none">
                    <label
                      htmlFor="consent"
                      className="cursor-pointer text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                    >
                      Acepto el tratamiento de mi nombre y correo para el envío de esta sugerencia, de acuerdo con la{' '}
                      <button
                        type="button"
                        onClick={() => setShowPolicy(true)}
                        className="text-primary hover:underline font-semibold"
                      >
                        Política de tratamiento de datos
                      </button>.
                    </label>
                  </div>
                </div>
              )}

              {status === 'error' && (
                <div className="flex items-center gap-2 rounded-lg border border-destructive/40 bg-destructive/10 px-3 py-2 text-sm text-destructive">
                  <AlertCircle className="h-4 w-4 shrink-0" />
                  {error}
                </div>
              )}

              <Button
                type="button"
                disabled={!valid || status === 'sending'}
                onClick={handleSubmit}
                className="bg-primary text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
              >
                {status === 'sending' ? 'Enviando…' : 'Enviar sugerencia'}
                <Send className="ml-1 h-4 w-4" />
              </Button>
            </div>
          )}
        </Card>
      </Reveal>

      <AnimatePresence>
        {showPolicy && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[100] flex items-center justify-center bg-black/60 p-4 backdrop-blur-sm"
            onClick={() => setShowPolicy(false)}
          >
            <motion.div
              initial={{ scale: 0.95, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.95, y: 20 }}
              onClick={(e) => e.stopPropagation()}
              className="relative w-full max-w-lg rounded-2xl border border-border bg-background p-6 shadow-2xl overflow-y-auto max-h-[90vh]"
            >
              <button 
                type="button"
                onClick={() => setShowPolicy(false)}
                className="absolute right-4 top-4 rounded-full p-1 text-muted-foreground hover:bg-muted hover:text-foreground transition-colors"
              >
                <X className="h-5 w-5" />
              </button>
              <h3 className="mb-4 text-xl font-bold text-primary">Política de Tratamiento de Datos</h3>
              <div className="space-y-4 text-sm text-muted-foreground">
                <p><strong>Qué datos se recogen:</strong> Solo recopilamos tu nombre y correo electrónico si decides incluirlos voluntariamente en este formulario.</p>
                <p><strong>Finalidad:</strong> Estos datos se utilizarán exclusivamente para recibir, revisar y, si es pertinente, contactarte respecto a tu sugerencia o reporte.</p>
                <p><strong>Carácter opcional:</strong> Puedes enviar tu sugerencia de manera completamente anónima omitiendo tu nombre y correo.</p>
                <p><strong>Consentimiento:</strong> Al marcar la casilla, consientes explícitamente el almacenamiento de estos datos junto a tu sugerencia. No compartimos, vendemos ni utilizamos tu información para fines publicitarios o de terceros.</p>
                <p><strong>Almacenamiento:</strong> Los datos se almacenarán temporalmente en la base de datos segura de nuestra plataforma.</p>
                <p className="mt-6 text-xs opacity-70">Esta política podrá actualizarse a medida que evolucione la plataforma.</p>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}
