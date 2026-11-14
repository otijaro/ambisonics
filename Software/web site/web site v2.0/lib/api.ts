// Cliente de API para el backend FastAPI (Papermill + notebooks).
// La URL base se configura con NEXT_PUBLIC_API_URL. Si no existe,
// se asume que el backend está en el mismo origen ("/api/...").

export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ?? ''

function parseApiError(d: any, defaultMsg: string): string {
  if (!d || !d.detail) return defaultMsg;
  if (typeof d.detail === 'string') return d.detail;
  if (Array.isArray(d.detail) && d.detail.length > 0) {
    const firstErr = d.detail[0];
    const loc = firstErr.loc ? firstErr.loc.join('.') : '';
    
    if (loc.includes('email')) {
      return 'Ingresa un correo electrónico válido.'
    }
    if (loc.includes('password')) {
      return 'La contraseña proporcionada no es válida o es muy corta.'
    }
    if (loc.includes('consent_given')) {
      return 'Debes aceptar el tratamiento de datos para crear una cuenta.'
    }
    
    return firstErr.msg || defaultMsg;
  }
  return defaultMsg;
}

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
  original_mode: boolean
}

function url(path: string) {
  if (path.startsWith('/static/') && typeof window !== 'undefined') {
    const backendBase = `${window.location.protocol}//${window.location.hostname}:8000`;
    return `${backendBase}${path}`;
  }
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
  form.append('original_mode', String(params.original_mode))
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

// --- Auth Endpoints ---

export interface User {
  id: number
  email: string
  name: string
  is_active: boolean
  created_at: string
}

function handle401(res: Response, parsedData: any) {
  if (res.status === 401) {
    if (parsedData && parsedData.detail === 'Sesión expirada por inactividad') {
      if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('session-expired'))
      }
    } else {
      if (typeof window !== 'undefined') {
        window.dispatchEvent(new CustomEvent('session-revoked'))
      }
    }
  }
}

export async function getMe(signal?: AbortSignal): Promise<User | null> {
  const res = await fetch(url('/api/auth/me'), {
    method: 'GET',
    credentials: 'include',
    signal,
    cache: 'no-store'
  })
  if (!res.ok) {
    if (res.status === 401) {
      try {
        const d = await res.clone().json()
        handle401(res, d)
      } catch {}
    }
    return null
  }
  return res.json()
}

export async function login(email: string, password: string): Promise<User> {
  const res = await fetch(url('/api/auth/login'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ email, password }),
  })
  if (!res.ok) {
    let msg = 'Credenciales inválidas'
    try { 
      const d = await res.json()
      msg = parseApiError(d, msg)
    } catch {}
    throw new Error(msg)
  }
  return res.json()
}

export interface RegisterResult {
  message: string
  recovery_code: string
}

export async function register(name: string, email: string, password: string, consent_given: boolean): Promise<RegisterResult> {
  const res = await fetch(url('/api/auth/register'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ name, email, password, consent_given }),
  })
  if (!res.ok) {
    let msg = 'No se pudo crear la cuenta. Inténtalo nuevamente.'
    try { 
      const d = await res.json()
      msg = parseApiError(d, msg)
    } catch {}
    throw new Error(msg)
  }
  return res.json()
}

export async function logout(): Promise<void> {
  const res = await fetch(url('/api/auth/logout'), {
    method: 'POST',
    credentials: 'include',
  })
  if (!res.ok) throw new Error('Error al cerrar sesión')
}

export async function changePassword(current_password: string, new_password: string, confirm_password: string) {
  const res = await fetch(url('/api/auth/change-password'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ current_password, new_password, confirm_password })
  })
  if (!res.ok) {
    let msg = 'Error al cambiar la contraseña'
    try {
      const d = await res.json()
      handle401(res, d)
      msg = parseApiError(d, msg)
    } catch {}
    throw new Error(msg)
  }
  return res.json()
}

export async function resetPassword(email: string, recovery_code: string, new_password: string, confirm_password: string) {
  const res = await fetch(url('/api/auth/reset-password'), {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ email, recovery_code, new_password, confirm_password })
  })
  if (!res.ok) {
    let msg = 'Error al restablecer la contraseña'
    try {
      const d = await res.json()
      msg = parseApiError(d, msg)
    } catch {}
    throw new Error(msg)
  }
  return res.json() // { message, new_recovery_code }
}

export async function generateRecoveryCode() {
  const res = await fetch(url('/api/auth/generate-recovery-code'), {
    method: 'POST',
    credentials: 'include',
  })
  if (!res.ok) {
    let msg = 'Error al generar el código'
    try {
      const d = await res.json()
      handle401(res, d)
      msg = parseApiError(d, msg)
    } catch {}
    throw new Error(msg)
  }
  return res.json() // { message, recovery_code }
}

// --- My Conversions Endpoint ---

export interface MyConversion {
  id: number
  original_filename: string
  input_mode: string
  status: 'processing' | 'completed' | 'failed'
  requested_at: string
  finished_at?: string | null
  processing_seconds?: number | null
  original_duration_seconds?: number | null
  files: {
    file_type: string
    storage_path?: string
    wavUrl?: string
    mp3Url?: string
  }[]
  is_available: boolean
}

export async function getMyConversions(signal?: AbortSignal): Promise<MyConversion[]> {
  const res = await fetch(url('/api/processing-requests/mine'), {
    method: 'GET',
    credentials: 'include',
    signal,
    cache: 'no-store'
  })
  if (!res.ok) {
    if (res.status === 401) {
      try {
        const d = await res.clone().json()
        handle401(res, d)
      } catch {}
    }
    throw new Error('Error al obtener tus conversiones')
  }
  return res.json()
}
