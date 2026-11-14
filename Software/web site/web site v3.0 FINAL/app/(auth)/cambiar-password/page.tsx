'use client'

import { useState, useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { changePassword, generateRecoveryCode, logout } from '@/lib/api'
import { useAuth } from '@/components/auth-provider'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { RecoveryCodeModal } from '@/components/recovery-code-modal'

export default function CambiarPasswordPage() {
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)
  
  const [generating, setGenerating] = useState(false)
  const [recoveryCode, setRecoveryCode] = useState<string | null>(null)
  
  const router = useRouter()
  const { user, refreshUser, isLoading, setUser } = useAuth()

  useEffect(() => {
    // Only redirect if there is no user and we are not in a success state
    if (!isLoading && !user && !success) {
      router.push('/login')
    }
  }, [user, isLoading, router, success])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    setSuccess('')
    
    if (newPassword !== confirmPassword) {
      setError('Las contraseñas no coinciden.')
      return
    }

    setLoading(true)

    try {
      await changePassword(currentPassword, newPassword, confirmPassword)
      setSuccess('Tu contraseña fue actualizada correctamente. Por seguridad, inicia sesión nuevamente.')
      setUser(null)
      setTimeout(() => {
        router.push('/login')
      }, 3000)
    } catch (err: any) {
      setError(err.message || 'Error al cambiar la contraseña.')
    } finally {
      setLoading(false)
    }
  }

  const handleGenerateCode = async () => {
    setGenerating(true)
    setError('')
    setSuccess('')
    try {
      const res = await generateRecoveryCode()
      setRecoveryCode(res.recovery_code)
    } catch (err: any) {
      setError(err.message || 'Error al generar código.')
    } finally {
      setGenerating(false)
    }
  }

  // Only hide the form if loading or if there's no user AND no success message
  if ((isLoading || !user) && !success) {
    return <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center p-4">Cargando...</div>
  }

  // If there is a success message, we can just show a simpler success screen or keep the form visible but disabled.
  // We'll keep the form but disable everything, or just let it render. Since user is null, the form logic won't work, but it redirects anyway.
  if (success) {
    return (
      <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center p-4">
        <div className="w-full max-w-md rounded-2xl glass p-8 text-center space-y-4">
          <h1 className="text-2xl font-semibold mb-2 text-green-500">¡Éxito!</h1>
          <p className="text-muted-foreground">{success}</p>
        </div>
      </div>
    )
  }

  return (
    <>
      <div className="flex min-h-[calc(100vh-4rem)] items-center justify-center p-4">
        <div className="w-full max-w-md rounded-2xl glass p-8 space-y-8">
          
          <div>
            <h1 className="text-2xl font-semibold mb-2">Seguridad de la cuenta</h1>
            <p className="text-sm text-muted-foreground mb-6">
              Cambia tu contraseña o genera un nuevo código de recuperación.
            </p>
            
            <form onSubmit={handleSubmit} className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="current">Contraseña actual</Label>
                <Input
                  id="current"
                  type="password"
                  required
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                  placeholder="••••••••"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="new">Nueva contraseña</Label>
                <Input
                  id="new"
                  type="password"
                  required
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  placeholder="••••••••"
                />
              </div>
              <div className="space-y-2">
                <Label htmlFor="confirm">Confirmar nueva contraseña</Label>
                <Input
                  id="confirm"
                  type="password"
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="••••••••"
                />
              </div>

              {error && <div className="text-sm text-red-500 font-medium">{error}</div>}
              {success && <div className="text-sm text-green-500 font-medium">{success}</div>}

              <Button type="submit" className="w-full mt-4" disabled={loading}>
                {loading ? 'Actualizando...' : 'Actualizar contraseña'}
              </Button>
            </form>
          </div>

          <div className="pt-6 border-t border-border">
            <h2 className="text-lg font-semibold mb-2">Código de recuperación</h2>
            <p className="text-sm text-muted-foreground mb-4">
              Si perdiste tu código de recuperación o eres un usuario antiguo, puedes generar uno nuevo. Al hacerlo, el código anterior dejará de funcionar.
            </p>
            <Button 
              variant="outline" 
              className="w-full" 
              onClick={handleGenerateCode} 
              disabled={generating}
            >
              {generating ? 'Generando...' : 'Generar nuevo código'}
            </Button>
          </div>
          
        </div>
      </div>
      
      <RecoveryCodeModal 
        code={recoveryCode} 
        onClose={() => setRecoveryCode(null)} 
      />
    </>
  )
}
