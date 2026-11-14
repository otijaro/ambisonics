'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { register, login } from '@/lib/api'
import { useAuth } from '@/components/auth-provider'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'

import { RecoveryCodeModal } from '@/components/recovery-code-modal'

export default function RegisterPage() {
  const [name, setName] = useState('')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [acceptTerms, setAcceptTerms] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [recoveryCode, setRecoveryCode] = useState<string | null>(null)
  
  const router = useRouter()
  const { refreshUser } = useAuth()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    
    if (password !== confirmPassword) {
      setError('Las contraseñas no coinciden.')
      return
    }

    if (!acceptTerms) {
      setError('Debes aceptar el tratamiento de tus datos personales para crear una cuenta.')
      return
    }

    setLoading(true)

    try {
      const res = await register(name, email, password, acceptTerms)
      await login(email, password)
      await refreshUser()
      setRecoveryCode(res.recovery_code)
    } catch (err: any) {
      setError(err.message || 'Error al crear la cuenta')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center p-4">
        <div className="w-full max-w-md rounded-2xl glass p-8">
          <h1 className="text-2xl font-semibold mb-2">Crear cuenta</h1>
          <p className="text-sm text-muted-foreground mb-6">
            Únete a Ambisonic para guardar tu historial de conversiones durante 24 horas.
          </p>

          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="name">Nombre</Label>
              <Input
                id="name"
                type="text"
                required
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Tu nombre"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Correo electrónico</Label>
              <Input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="tu@correo.com"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Contraseña</Label>
              <Input
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="confirmPassword">Confirmar contraseña</Label>
              <Input
                id="confirmPassword"
                type="password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••"
              />
            </div>

            <div className="flex items-start space-x-2 pt-2">
              <input 
                type="checkbox"
                id="terms" 
                checked={acceptTerms} 
                onChange={(e) => setAcceptTerms(e.target.checked)}
                className="mt-1 h-4 w-4 rounded border-gray-300 text-primary focus:ring-primary"
              />
              <div className="grid gap-1.5 leading-none">
                <label
                  htmlFor="terms"
                  className="text-sm font-medium leading-tight peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                >
                  Acepto el tratamiento de mis datos personales para la creación y administración de mi cuenta.
                </label>
              </div>
            </div>

            {error && <div className="text-sm text-red-500 font-medium">{error}</div>}

            <Button type="submit" className="w-full mt-4" disabled={loading}>
              {loading ? 'Creando cuenta...' : 'Crear cuenta'}
            </Button>
          </form>

          <div className="mt-6 text-center text-sm text-muted-foreground">
            ¿Ya tienes una cuenta?{' '}
            <Link href="/login" className="text-primary hover:underline font-medium">
              Inicia sesión
            </Link>
          </div>
        </div>
      </div>
      
      <RecoveryCodeModal 
        code={recoveryCode} 
        onClose={() => router.push('/')} 
      />
    </>
  )
}
