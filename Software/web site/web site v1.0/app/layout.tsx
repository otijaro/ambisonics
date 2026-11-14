
import type { Metadata, Viewport } from 'next'
import { Geist, Geist_Mono } from 'next/font/google'
import { Navbar } from '@/components/navbar'
import { Footer } from '@/components/footer'
import './globals.css'

const geistSans = Geist({ subsets: ['latin'], variable: '--font-geist-sans' })
const geistMono = Geist_Mono({ subsets: ['latin'], variable: '--font-geist-mono' })

export const metadata: Metadata = {
  title: 'Ambisonic — Convierte tu audio, expande tu mundo',
  description:
    'Transforma audio estéreo en experiencias ambisónicas y binaurales de alta calidad. Más inmersión, más realismo, más emoción.',
  generator: 'v0.app',
}

export const viewport: Viewport = {
  colorScheme: 'dark',
  themeColor: '#09090b',
}

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode
}>) {
  return (
    <html lang="es" className={`dark ${geistSans.variable} ${geistMono.variable}`}>
      <body className="min-h-screen bg-background font-sans text-foreground antialiased">
        <Navbar />
        <main>{children}</main>
        <Footer />

      </body>
    </html>
  )
}
