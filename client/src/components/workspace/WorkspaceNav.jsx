import { useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../../auth/AuthContext'
import '../../workspace.css'

export default function WorkspaceNav() {
  const { logout } = useAuth()
  const navigate = useNavigate()
  const [leaving, setLeaving] = useState(false)
  const [error, setError] = useState('')
  async function signOut() {
    setLeaving(true); setError('')
    try { await logout(); navigate('/login', { replace: true }) }
    catch (failure) { setError(failure.message); setLeaving(false) }
  }
  return <div className="workspace-navigation"><nav aria-label="Tu espacio" className="workspace-nav"><NavLink to="/dashboard" end>↗ Dashboard</NavLink><NavLink to="/groups">▦ Mis grupos</NavLink></nav><button className="workspace-logout" disabled={leaving} onClick={signOut}>{leaving ? 'Cerrando sesión…' : 'Cerrar sesión'}</button>{error && <p role="alert" className="form-error">{error}</p>}</div>
}
