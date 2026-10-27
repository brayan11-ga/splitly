import { useEffect } from 'react'
import { Link } from 'react-router-dom'
import { Arrow } from '../components/LandingUI'
export default function PendingPage({ kind }) {
  const missing = kind === 'missing'
  const title = missing ? 'Esta página no existe.' : kind === 'login' ? 'Iniciar sesión' : 'Crear tu cuenta'
  useEffect(() => { document.title = `${title} · Splitly`; window.scrollTo(0, 0) }, [title])
  return <main id="contenido" className="shell pending-page"><p className="eyebrow text-lime">{missing ? '404 / Ruta no encontrada' : 'Próximamente / Acceso pendiente'}</p><h1>{title}<span className="text-lime">↗</span></h1><p>{missing ? 'Vuelve al inicio para conocer Splitly.' : 'Esta es una página provisional. El registro y el inicio de sesión todavía no están disponibles; no se recopilan datos personales.'}</p><Link className="action action-primary" to="/">Volver al inicio <Arrow /></Link></main>
}
