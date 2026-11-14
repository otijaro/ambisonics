'use client'

import React, { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { ShieldAlert, Copy, Check } from 'lucide-react'
import { Button } from '@/components/ui/button'

interface Props {
  code: string | null
  onClose: () => void
}

export function RecoveryCodeModal({ code, onClose }: Props) {
  const [copied, setCopied] = useState(false)
  const [acknowledged, setAcknowledged] = useState(false)

  if (!code) return null

  const handleCopy = () => {
    navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-[200] flex items-center justify-center bg-background/80 backdrop-blur-sm p-4"
      >
        <motion.div
          initial={{ scale: 0.95, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          exit={{ scale: 0.95, opacity: 0 }}
          className="w-full max-w-md overflow-hidden rounded-2xl border border-border bg-card p-6 shadow-2xl glass"
        >
          <div className="flex flex-col text-center items-center">
            <div className="mb-4 rounded-full bg-orange-500/20 p-3 text-orange-500">
              <ShieldAlert className="h-8 w-8" />
            </div>
            <h2 className="mb-2 text-xl font-bold text-foreground">
              Código de Recuperación
            </h2>
            <p className="mb-4 text-sm text-muted-foreground">
              Guarda tu código de recuperación. Este código es la única forma de recuperar tu cuenta si olvidas la contraseña. No podremos mostrártelo nuevamente después de cerrar esta ventana.
            </p>
            
            <div className="flex w-full items-center justify-between bg-muted rounded-xl p-4 mb-6">
              <code className="text-lg font-mono font-bold tracking-widest text-foreground">{code}</code>
              <Button variant="ghost" size="sm" onClick={handleCopy} className="ml-2 gap-2">
                {copied ? <Check className="h-4 w-4" /> : <Copy className="h-4 w-4" />}
                {copied ? 'Copiado' : 'Copiar'}
              </Button>
            </div>

            <div className="flex items-start space-x-2 text-left mb-6 w-full">
              <input 
                type="checkbox"
                id="ack" 
                checked={acknowledged} 
                onChange={(e) => setAcknowledged(e.target.checked)}
                className="mt-1 h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
              />
              <label
                htmlFor="ack"
                className="text-sm font-medium leading-tight cursor-pointer"
              >
                Entiendo que debo guardar este código para poder recuperar mi cuenta.
              </label>
            </div>

            <Button 
              className="w-full" 
              onClick={onClose}
              disabled={!acknowledged}
            >
              Continuar
            </Button>
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  )
}
