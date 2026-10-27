import { Link } from 'react-router-dom'
export function Wordmark() {
  return <span className="wordmark">SPLITLY<span className="text-lime">·</span></span>
}
export function SiteHeader() {
  return <header className="site-header"><div className="shell header-inner"><Link to="/" aria-label="Splitly, inicio"><Wordmark /></Link><nav aria-label="Navegación principal" className="main-nav"><a href="/#como-funciona">Cómo funciona</a><a href="/#beneficios">Beneficios</a></nav><nav aria-label="Acceso" className="access-nav"><Link to="/login">Iniciar sesión</Link><Link className="nav-register" to="/register">Registrarse <span aria-hidden="true">↗</span></Link></nav></div></header>
}
export function SiteFooter() {
  return <footer className="site-footer"><div className="shell"><div className="footer-top"><div><Link to="/" aria-label="Splitly, inicio"><Wordmark /></Link><p>Más planes juntos.<br />Menos cuentas pendientes.</p></div><nav aria-label="Producto"><span className="eyebrow">Explora</span><a href="/#como-funciona">Cómo funciona</a><a href="/#beneficios">Beneficios</a><a href="/#ejemplo">Ver un ejemplo</a></nav><nav aria-label="Cuenta"><span className="eyebrow">El siguiente paso</span><Link to="/login">Iniciar sesión</Link><Link to="/register">Registrarse</Link><span className="text-lime">Colombia · COP</span></nav></div><div className="footer-bottom eyebrow"><span>© 2026 Splitly · Hecho para compartir</span><span>Prototipo en desarrollo · Solo datos ficticios</span></div></div></footer>
}

