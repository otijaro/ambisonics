'use client'

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react'
import { getMe, User } from '@/lib/api'

interface AuthContextType {
  user: User | null
  isLoading: boolean
  setUser: (user: User | null) => void
  refreshUser: () => Promise<void>
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

import { useRouter, usePathname } from 'next/navigation'
import { motion, AnimatePresence } from 'framer-motion'
import { AlertCircle } from 'lucide-react'
import { buttonVariants } from '@/components/ui/button'

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUserState] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [sessionExpired, setSessionExpired] = useState(false)
  
  const router = useRouter()
  const pathname = usePathname()

  const refreshUser = useCallback(async () => {
    try {
      setIsLoading(true)
      const userData = await getMe()
      setUserState(userData)
    } catch (error) {
      console.error('Failed to fetch user:', error)
      setUserState(null)
    } finally {
      setIsLoading(false)
    }
  }, [])

  useEffect(() => {
    refreshUser()
  }, [refreshUser])
  
  useEffect(() => {
    const handleExpired = () => {
      setUserState(null)
      if (pathname !== '/login') {
        setSessionExpired(true)
      }
    }

    const handleRevoked = () => {
      setUserState(null)
    }
    
    window.addEventListener('session-expired', handleExpired)
    window.addEventListener('session-revoked', handleRevoked)
    return () => {
      window.removeEventListener('session-expired', handleExpired)
      window.removeEventListener('session-revoked', handleRevoked)
    }
  }, [pathname])

  return (
    <AuthContext.Provider value={{ user, isLoading, setUser: setUserState, refreshUser }}>
      {children}
      
      <AnimatePresence>
        {sessionExpired && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[100] flex items-center justify-center bg-background/80 backdrop-blur-sm p-4"
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              exit={{ scale: 0.95, opacity: 0 }}
              className="w-full max-w-md overflow-hidden rounded-2xl border border-border bg-card p-6 shadow-2xl glass"
            >
              <div className="flex flex-col items-center text-center">
                <div className="mb-4 rounded-full bg-red-500/20 p-3 text-red-500">
                  <AlertCircle className="h-8 w-8" />
                </div>
                <h2 className="mb-2 text-xl font-bold text-foreground">
                  Sesión cerrada por inactividad
                </h2>
                <p className="mb-6 text-sm text-muted-foreground">
                  Por seguridad, tu sesión se cerró después de 15 minutos sin actividad. Inicia sesión nuevamente para continuar.
                </p>
                <div className="flex w-full flex-col gap-3 sm:flex-row">
                  <button
                    onClick={() => setSessionExpired(false)}
                    className={buttonVariants({ variant: 'outline', className: 'flex-1' })}
                  >
                    Cerrar
                  </button>
                  <button
                    onClick={() => {
                      setSessionExpired(false)
                      router.push('/login')
                    }}
                    className={buttonVariants({ variant: 'default', className: 'flex-1' })}
                  >
                    Iniciar sesión
                  </button>
                </div>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
