import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import WorkspaceNav from '../components/workspace/WorkspaceNav'
import GroupsPanel from '../components/workspace/GroupsPanel'
import '../auth.css'

export default function DashboardPage() {
  const { user } = useAuth()
  const { state } = useLocation()
  useEffect(() => {
    document.title = 'Tu espacio · Splitly'
    window.scrollTo(0, 0)
  }, [])
  return <main id="contenido" className="shell workspace-page"><WorkspaceNav /><header className="workspace-heading"><p className="eyebrow text-lime">Tu espacio / Splitly</p><h1 data-page-heading tabIndex={-1}>Hola, {user.full_name}.</h1><p>Tus planes, en un solo lugar.</p></header>{state?.notice && <p role="status" className="workspace-success">{state.notice}</p>}<GroupsPanel preview /></main>
}
