import { Navigate } from 'react-router-dom'
import { useAuth } from './AuthContext'

export function AuthStatus() {
  const { status, refresh } = useAuth()
  return <main id="contenido" className="shell auth-status" aria-live="polite">
    {status === 'error' ? <><h1>No pudimos comprobar tu sesión.</h1><p>Comprueba tu conexión y vuelve a intentarlo.</p><button className="action action-primary" onClick={() => refresh()}>Reintentar</button></> : <p role="status">Comprobando tu sesión…</p>}
  </main>
}
export default function ProtectedRoute({ children }) {
  const { status } = useAuth()
  if (status === 'loading' || status === 'error') return <AuthStatus />
  if (status !== 'authenticated') return <Navigate to="/login" replace />
  return children
}
