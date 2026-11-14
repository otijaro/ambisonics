'use client'

import { useState } from 'react'
import { useRouter } from 'next/navigation'
import Link from 'next/link'
import { resetPassword } from '@/lib/api'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { RecoveryCodeModal } from '@/components/recovery-code-modal'

export default function RecuperarPasswordPage() {
  const [email, setEmail] = useState('')
  const [recoveryCodeInput, setRecoveryCodeInput] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [newRecoveryCode, setNewRecoveryCode] = useState<string | null>(null)
  
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    
    if (password !== confirmPassword) {
      setError('Las contraseñas no coinciden.')
      return
    }

    setLoading(true)

    try {
      const res = await resetPassword(email, recoveryCodeInput, password, confirmPassword)
      setNewRecoveryCode(res.new_recovery_code)
    } catch (err: any) {
      setError(err.message || 'No fue posible verificar los datos de recuperación.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <>
      <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center p-4">
        <div className="w-full max-w-md rounded-2xl glass p-8">
          <h1 className="text-2xl font-semibold mb-2">Recuperar contraseña</h1>
          <p className="text-sm text-muted-foreground mb-6">
            Ingresa tu correo y el código de recuperación que guardaste al crear tu cuenta para restablecer tu contraseña.
          </p>

          <form onSubmit={handleSubmit} className="space-y-4">
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
              <Label htmlFor="code">Código de recuperación</Label>
              <Input
                id="code"
                type="text"
                required
                value={recoveryCodeInput}
                onChange={(e) => setRecoveryCodeInput(e.target.value)}
                placeholder="XXXX-XXXX-XXXX-XXXX"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="password">Nueva Contraseña</Label>
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
              <Label htmlFor="confirmPassword">Confirmar nueva contraseña</Label>
              <Input
                id="confirmPassword"
                type="password"
                required
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="••••••••"
              />
            </div>

            {error && <div className="text-sm text-red-500 font-medium">{error}</div>}

            <Button type="submit" className="w-full mt-4" disabled={loading}>
              {loading ? 'Restableciendo...' : 'Restablecer contraseña'}
            </Button>
          </form>

          <div className="mt-6 text-center text-sm text-muted-foreground">
            <Link href="/login" className="text-primary hover:underline font-medium">
              Volver a iniciar sesión
            </Link>
          </div>
        </div>
      </div>
      
      <RecoveryCodeModal 
        code={newRecoveryCode} 
        onClose={() => router.push('/login')} 
      />
    </>
  )
}
