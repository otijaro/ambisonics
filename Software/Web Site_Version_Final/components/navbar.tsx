'use client'

import Link from 'next/link'
import { usePathname } from 'next/navigation'
import { useState, useRef, useEffect } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { Menu, X, ArrowRight } from 'lucide-react'
import { buttonVariants } from '@/components/ui/button'
import { Logo } from '@/components/logo'
import { HealthIndicator } from '@/components/health-indicator'
import { useAuth } from '@/components/auth-provider'
import { logout } from '@/lib/api'
import { useRouter } from 'next/navigation'
import { cn } from '@/lib/utils'
const links = [
  { href: '/', label: 'Inicio' },
  { href: '/conversor', label: 'Conversor' },
  { href: '/demo', label: 'Demo interactiva' },
  { href: '/guia', label: 'Guía' },
  { href: '/acerca-de', label: 'Acerca de' },
  { href: '/sugerencias', label: 'Sugerencias' },
]

function UserDropdown({ user, onLogout }: { user: any, onLogout: () => void }) {
  const [isOpen, setIsOpen] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => { if (e.key === 'Escape') setIsOpen(false) }
    const handleClickOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('keydown', handleEscape)
    document.addEventListener('mousedown', handleClickOutside)
    return () => {
      document.removeEventListener('keydown', handleEscape)
      document.removeEventListener('mousedown', handleClickOutside)
    }
  }, [])

  return (
    <div className="relative" ref={dropdownRef}>
      <button 
        onClick={() => setIsOpen(!isOpen)}
        className={cn(buttonVariants({ variant: 'outline', size: 'sm' }), "gap-1")}
        aria-expanded={isOpen}
      >
        {user.name} <span className="text-xs opacity-70">▾</span>
      </button>
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 8, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 8, scale: 0.95 }}
            transition={{ duration: 0.15 }}
            className="absolute right-0 top-full mt-2 w-56 origin-top-right rounded-xl border border-primary/30 bg-[#121018] shadow-[0_10px_40px_-10px_rgba(0,0,0,0.8)] overflow-hidden z-50 ring-1 ring-black/20"
          >
            <div className="px-4 py-3 border-b border-white/10 bg-white/[0.02]">
              <p className="text-sm font-semibold text-white truncate">{user.name}</p>
              <p className="text-xs text-white/60 truncate mt-0.5">{user.email}</p>
            </div>
            <div className="p-1.5 space-y-0.5 border-b border-white/5">
              <Link
                href="/mis-conversiones"
                onClick={() => setIsOpen(false)}
                className="flex w-full items-center rounded-md px-3 py-2 text-sm text-white/80 hover:bg-white/10 hover:text-white transition-colors"
              >
                Mis conversiones
              </Link>
              <Link
                href="/cambiar-password"
                onClick={() => setIsOpen(false)}
                className="flex w-full items-center rounded-md px-3 py-2 text-sm text-white/80 hover:bg-white/10 hover:text-white transition-colors"
              >
                Cambiar contraseña
              </Link>
            </div>
            <div className="p-1.5">
              <button
                onClick={() => { setIsOpen(false); onLogout(); }}
                className="flex w-full items-center rounded-md px-3 py-2 text-sm text-red-400 hover:bg-red-500/15 hover:text-red-300 transition-colors font-medium"
              >
                Cerrar sesión
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  )
}

export function Navbar() {
  const pathname = usePathname()
  const router = useRouter()
  const [open, setOpen] = useState(false)
  const { user, isLoading, refreshUser } = useAuth()

  const handleLogout = async () => {
    try {
      await logout()
      await refreshUser()
      router.push('/')
    } catch (e) {
      console.error(e)
    }
  }

  return (
    <header className="sticky inset-x-0 top-0 z-50 bg-background border-b border-border">
      <div>
        <nav className="mx-auto flex h-16 max-w-7xl items-center justify-between gap-4 px-4 sm:px-6 lg:px-8">
          <Link href="/" aria-label="Ambisonic — inicio" onClick={() => setOpen(false)}>
            <Logo />
          </Link>

          <ul className="hidden items-center gap-1 lg:flex">
            {links.map((link) => {
              const active = pathname === link.href
              return (
                <li key={link.href}>
                  <Link
                    href={link.href}
                    className={cn(
                      'relative rounded-full px-3.5 py-2 text-sm transition-colors',
                      active ? 'text-foreground' : 'text-muted-foreground hover:text-foreground',
                    )}
                  >
                    {link.label}
                    {active && (
                      <motion.span
                        layoutId="nav-underline"
                        className="absolute inset-x-3 -bottom-px h-0.5 rounded-full bg-primary"
                      />
                    )}
                  </Link>
                </li>
              )
            })}
          </ul>

          <div className="flex items-center gap-3">
            <HealthIndicator className="hidden md:flex" />

            {!isLoading && user ? (
              <div className="hidden items-center gap-3 md:flex">
                <UserDropdown user={user} onLogout={handleLogout} />
              </div>
            ) : !isLoading && !user ? (
              <div className="hidden items-center gap-2 md:flex">
                <Link
                  href="/login"
                  className={cn(buttonVariants({ variant: 'ghost', size: 'sm' }))}
                >
                  Iniciar sesión
                </Link>
                <Link
                  href="/crear-cuenta"
                  className={cn(buttonVariants({ variant: 'outline', size: 'sm' }))}
                >
                  Crear cuenta
                </Link>
              </div>
            ) : null}

            <Link
              href="/conversor"
              className={cn(
                buttonVariants({ variant: 'default' }),
                'hidden h-10 bg-primary px-4 text-primary-foreground hover:bg-primary/90 sm:inline-flex',
              )}
            >
              Comenzar
              <ArrowRight className="ml-1 h-4 w-4" />
            </Link>
            <button
              className="inline-flex h-10 w-10 items-center justify-center rounded-lg text-foreground lg:hidden"
              onClick={() => setOpen((v) => !v)}
              aria-label={open ? 'Cerrar menú' : 'Abrir menú'}
              aria-expanded={open}
            >
              {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
          </div>
        </nav>
      </div>

      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.2 }}
            className="glass mx-4 mt-2 rounded-2xl p-3 lg:hidden"
          >
            <ul className="flex flex-col">
              {links.map((link) => {
                const active = pathname === link.href
                return (
                  <li key={link.href}>
                    <Link
                      href={link.href}
                      onClick={() => setOpen(false)}
                      className={cn(
                        'block rounded-xl px-4 py-3 text-sm transition-colors',
                        active ? 'bg-accent text-foreground' : 'text-muted-foreground hover:bg-accent/60 hover:text-foreground',
                      )}
                    >
                      {link.label}
                    </Link>
                  </li>
                )
              })}
              <li className="mt-2 px-1">
                <HealthIndicator />
              </li>
              {!isLoading && user ? (
                  <div className="mt-4 border-t border-border/50 pt-4">
                    <div className="px-4 mb-2">
                      <p className="text-sm font-medium text-foreground truncate">{user.name}</p>
                      <p className="text-xs text-muted-foreground truncate">{user.email}</p>
                    </div>
                    <li>
                      <Link
                        href="/mis-conversiones"
                        onClick={() => setOpen(false)}
                        className="block rounded-xl px-4 py-3 text-sm transition-colors text-muted-foreground hover:bg-accent/60 hover:text-foreground"
                      >
                        Mis conversiones
                      </Link>
                    </li>
                    <li>
                      <Link
                        href="/cambiar-password"
                        onClick={() => setOpen(false)}
                        className="block rounded-xl px-4 py-3 text-sm transition-colors text-muted-foreground hover:bg-accent/60 hover:text-foreground"
                      >
                        Cambiar contraseña
                      </Link>
                    </li>
                    <li>
                      <button
                        onClick={() => { setOpen(false); handleLogout(); }}
                        className="w-full text-left rounded-xl px-4 py-3 text-sm transition-colors text-red-400 hover:bg-red-500/10 hover:text-red-500"
                      >
                        Cerrar sesión
                      </button>
                    </li>
                  </div>
              ) : !isLoading && !user ? (
                <>
                  <li className="mt-4">
                    <Link
                      href="/login"
                      onClick={() => setOpen(false)}
                      className="block rounded-xl px-4 py-3 text-sm transition-colors text-muted-foreground hover:bg-accent/60 hover:text-foreground"
                    >
                      Iniciar sesión
                    </Link>
                  </li>
                  <li>
                    <Link
                      href="/crear-cuenta"
                      onClick={() => setOpen(false)}
                      className="block rounded-xl px-4 py-3 text-sm transition-colors text-muted-foreground hover:bg-accent/60 hover:text-foreground"
                    >
                      Crear cuenta
                    </Link>
                  </li>
                </>
              ) : null}
            </ul>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  )
}
