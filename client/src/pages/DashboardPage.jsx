import { useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { apiRequest } from '../services/api'
import '../auth.css'

export default function DashboardPage() {
  const { user, logout } = useAuth()
  const navigate = useNavigate()
  const { state } = useLocation()
  const [groups, setGroups] = useState([])
  const [status, setStatus] = useState('loading')
  const [error, setError] = useState('')
  const [leaving, setLeaving] = useState(false)
  const [attempt, setAttempt] = useState(0)
  useEffect(() => {
    document.title = 'Mis grupos · Splitly'
    const controller = new AbortController()
    apiRequest('/groups', { signal: controller.signal }).then(data => {
      setGroups(data); setStatus('success')
    }).catch(failure => {
      if (failure.name !== 'AbortError') { setError(failure.message); setStatus('error') }
    })
    return () => controller.abort()
  }, [attempt])
  async function signOut() {
    setLeaving(true); setError('')
    try { await logout(); navigate('/login', { replace: true }) }
    catch (failure) { setError(failure.message); setLeaving(false) }
  }
  return <main id="contenido" className="shell dashboard-page"><div className="dashboard-heading"><div><p className="eyebrow text-lime">Tu espacio / Splitly</p><h1>Hola, {user.full_name}.</h1><p>Tus planes, en un solo lugar.</p></div><button className="action action-secondary" disabled={leaving} onClick={signOut}>{leaving ? 'Cerrando sesión…' : 'Cerrar sesión'}</button></div>
    {state?.notice && <p role="status" className="auth-success">{state.notice}</p>}{error && <p className="form-error" role="alert">{error}</p>}
    <section className="dashboard-groups" aria-labelledby="groups-heading"><h2 id="groups-heading">Mis grupos</h2>{status === 'loading' && <p role="status">Cargando tus grupos…</p>}{status === 'error' && <button className="action action-secondary" onClick={() => { setStatus('loading'); setError(''); setAttempt(attempt + 1) }}>Reintentar</button>}
      {status === 'success' && (groups.length ? <ul className="dashboard-list">{groups.map(group => <li key={group.id}><span className="text-lime" aria-hidden="true">↗</span><h3>{group.name}</h3><span className="eyebrow">Grupo personal</span></li>)}</ul> : <div className="dashboard-empty"><span className="text-lavender" aria-hidden="true">↗</span><h3>El próximo plan empieza aquí.</h3><p>Aún no tienes grupos. Tu sesión está lista; la gestión de grupos en esta pantalla llegará en la siguiente iteración.</p></div>)}
    </section></main>
}
