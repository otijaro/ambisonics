import type { Metadata } from 'next'
import { GuiaContent } from '@/components/guia/guia-content'

export const metadata: Metadata = {
  title: 'Guía — Ambisonic',
  description: 'Documentación sobre audio estéreo, ambisónico, coordenadas del oyente y canales W X Y Z.',
}

export default function GuiaPage() {
  return <GuiaContent />
}
