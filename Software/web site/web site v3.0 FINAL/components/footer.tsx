import Link from 'next/link'
import { Logo } from '@/components/logo'

const quickLinks = [
  { href: '/conversor', label: 'Conversor' },
  { href: '/demo', label: 'Demo interactiva' },
  { href: '/guia', label: 'Guía' },
  { href: '/acerca-de', label: 'Acerca de' },
]

export function Footer() {
  return (
    <footer className="border-t border-border bg-background/60">
      <div className="mx-auto grid max-w-7xl gap-10 px-4 py-14 sm:px-6 md:grid-cols-3 lg:px-8">
        <div className="space-y-4">
          <Logo />
          <p className="max-w-xs text-sm leading-relaxed text-muted-foreground">
            Convierte audio estéreo en experiencias espaciales ambisónicas y binaurales de alta calidad.
          </p>
        </div>

        <div>
          <h3 className="text-sm font-semibold text-foreground">Enlaces rápidos</h3>
          <ul className="mt-4 space-y-2.5">
            {quickLinks.map((link) => (
              <li key={link.href}>
                <Link href={link.href} className="text-sm text-muted-foreground transition-colors hover:text-foreground">
                  {link.label}
                </Link>
              </li>
            ))}
          </ul>
        </div>

        <div>
          <h3 className="text-sm font-semibold text-foreground">Contacto y créditos</h3>
          <ul className="mt-4 space-y-2.5 text-sm text-muted-foreground">
            <li>
              <Link href="/sugerencias" className="transition-colors hover:text-foreground">
                Enviar sugerencia
              </Link>
            </li>
            <li>
              <Link href="/acerca-de" className="transition-colors hover:text-foreground">
                Créditos del proyecto
              </Link>
            </li>
            <li>Universidad Industrial de Santander</li>
          </ul>
        </div>
      </div>

      <div className="border-t border-border">
        <div className="mx-auto max-w-7xl px-4 py-6 text-center text-xs text-muted-foreground sm:px-6 lg:px-8">
          © {new Date().getFullYear()} Ambisonic. Proyecto universitario — Universidad Industrial de Santander.
        </div>
      </div>
    </footer>
  )
}
