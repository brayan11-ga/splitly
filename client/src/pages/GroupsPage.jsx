import { useEffect } from 'react'
import { useLocation } from 'react-router-dom'
import WorkspaceNav from '../components/workspace/WorkspaceNav'
import GroupsPanel from '../components/workspace/GroupsPanel'

export default function GroupsPage() {
  const { state } = useLocation()
  useEffect(() => { document.title = 'Mis grupos · Splitly'; window.scrollTo(0, 0) }, [])
  return <main id="contenido" className="shell workspace-page"><WorkspaceNav /><header className="workspace-heading"><p className="eyebrow text-lavender">Colectivos / Gestión de grupos</p><h1 data-page-heading tabIndex={-1}>Tus grupos.<br /><span className="text-lime">Tus reglas.</span></h1><p>Un lugar para cada viaje, cada casa y cada plan compartido.</p></header>{state?.notice && <p role="status" className="workspace-success">{state.notice}</p>}<GroupsPanel /></main>
}
