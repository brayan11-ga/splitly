const API_BASE = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '')
let csrfToken = null
const unauthorizedListeners = new Set()

export class ApiError extends Error {
  constructor(message, status) { super(message); this.status = status }
}
export function setCsrfToken(token) { csrfToken = token }
export function onUnauthorized(callback) {
  unauthorizedListeners.add(callback)
  return () => unauthorizedListeners.delete(callback)
}

export async function apiRequest(path, { method = 'GET', body, signal } = {}) {
  const headers = {}
  if (body !== undefined) headers['Content-Type'] = 'application/json'
  if (!['GET', 'HEAD'].includes(method)) headers['X-CSRF-Token'] = csrfToken || 'bootstrap'
  let response
  try {
    response = await fetch(`${API_BASE}/api${path}`, {
      method, credentials: 'include', cache: 'no-store', headers, signal,
      ...(body !== undefined ? { body: JSON.stringify(body) } : {}),
    })
  } catch (error) {
    if (error.name === 'AbortError') throw error
    throw new ApiError('No pudimos conectar con Splitly. Inténtalo de nuevo.', 0)
  }
  if (!response.ok) {
    if (response.status === 401 && !['/auth/login', '/auth/register'].includes(path)) {
      csrfToken = null
      unauthorizedListeners.forEach(callback => callback())
    }
    const messages = {
      401: path === '/auth/login' ? 'Correo o contraseña incorrectos.' : 'Tu sesión terminó. Inicia sesión de nuevo.',
      403: 'No pudimos validar esta solicitud. Recarga la página e inténtalo de nuevo.',
      404: 'No encontramos este recurso o no tienes acceso a él.',
      409: path === '/auth/register' ? 'No pudimos registrar ese correo. Prueba iniciar sesión.' : 'Hay registros relacionados que impiden esta operación.',
      422: 'Revisa los datos del formulario.',
      429: 'Demasiados intentos. Espera antes de volver a intentarlo.',
    }
    throw new ApiError(messages[response.status] || 'No pudimos completar la solicitud. Inténtalo de nuevo.', response.status)
  }
  if (response.status === 204) return null
  try { return await response.json() }
  catch { throw new ApiError('Recibimos una respuesta inesperada. Inténtalo de nuevo.', 0) }
}
