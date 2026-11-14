// Cliente de API para el backend FastAPI (Papermill + notebooks).
// La URL base se configura con NEXT_PUBLIC_API_URL. Si no existe,
// se asume que el backend está en el mismo origen ("/api/...").

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? ''

export type ConversionFormatKey =
  | 'binaural'
  | 'binaural_3d'
  | 'cuad_horizontal'
  | 'cuad_altura'
  | 'horizontal_3d'
  | 'altura_3d'

export interface ConversionOutput {
  key: ConversionFormatKey
  wavUrl?: string
  mp3Url?: string
  durationSeconds?: number
}

export interface ConvertResponse {
  outputs: ConversionOutput[]
  processing_seconds?: number
  original_duration_seconds?: number
}

export interface DemoResponse {
  binaural?: { wavUrl?: string; mp3Url?: string }
  binaural_3d?: { wavUrl?: string; mp3Url?: string }
}

export interface DemoParams {
  direccion: number
  altura: number
  apertura: number
  movimiento: number
}

function url(path: string) {
  return `${API_BASE_URL}${path}`
}

/** GET /api/health — indicador de estado del servidor. */
export async function checkHealth(signal?: AbortSignal): Promise<boolean> {
  try {
    const res = await fetch(url('/api/health'), { signal, cache: 'no-store' })
    return res.ok
  } catch {
    return false
  }
}

/** POST /api/convert — multipart/form-data { audio, mode }. */
export async function convertAudio(
  audio: File,
  mode: 'stereo' | 'tetra_4mic' = 'stereo',
  signal?: AbortSignal
): Promise<ConvertResponse> {
  const form = new FormData()
  form.append('audio', audio)
  form.append('mode', mode)
  const res = await fetch(url('/api/convert'), { method: 'POST', body: form, signal })
  if (!res.ok) {
    const errText = await res.text().catch(() => '')
    let message = `Error al convertir el audio (${res.status})`
    try {
      const parsed = JSON.parse(errText)
      if (parsed.detail) message = parsed.detail
    } catch {}
    throw new Error(message)
  }
  const data: ConvertResponse = await res.json()
  data.outputs = data.outputs.map((o) => ({
    ...o,
    wavUrl: o.wavUrl && o.wavUrl.startsWith('/') ? url(o.wavUrl) : o.wavUrl,
    mp3Url: o.mp3Url && o.mp3Url.startsWith('/') ? url(o.mp3Url) : o.mp3Url,
  }))
  return data
}

/** POST /api/demo — multipart/form-data { audio, direccion, altura, apertura, movimiento }. */
export async function runDemo(audio: File, params: DemoParams, signal?: AbortSignal): Promise<DemoResponse> {
  const form = new FormData()
  form.append('audio', audio)
  form.append('direccion', String(params.direccion))
  form.append('altura', String(params.altura))
  form.append('apertura', String(params.apertura))
  form.append('movimiento', String(params.movimiento))
  const res = await fetch(url('/api/demo'), { method: 'POST', body: form, signal })
  if (!res.ok) throw new Error(`Error al ejecutar la demo (${res.status})`)
  const data: DemoResponse = await res.json()
  const fixUrl = (u?: string) => (u && u.startsWith('/') ? url(u) : u)
  if (data.binaural) {
    data.binaural.wavUrl = fixUrl(data.binaural.wavUrl)
    data.binaural.mp3Url = fixUrl(data.binaural.mp3Url)
  }
  if (data.binaural_3d) {
    data.binaural_3d.wavUrl = fixUrl(data.binaural_3d.wavUrl)
    data.binaural_3d.mp3Url = fixUrl(data.binaural_3d.mp3Url)
  }
  return data
}

export interface FeedbackPayload {
  nombre: string
  correo: string
  mensaje: string
}

/** POST /api/feedback — { nombre, correo, mensaje }. */
export async function sendFeedback(payload: FeedbackPayload, signal?: AbortSignal): Promise<void> {
  const res = await fetch(url('/api/feedback'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
    signal,
  })
  if (!res.ok) throw new Error(`Error al enviar la sugerencia (${res.status})`)
}
