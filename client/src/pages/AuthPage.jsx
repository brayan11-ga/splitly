import { useEffect, useState } from 'react'
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom'
import { useAuth } from '../auth/AuthContext'
import { AuthStatus } from '../auth/ProtectedRoute'
import { Arrow } from '../components/LandingUI'
import '../auth.css'

function PasswordField({ name, label, value, onChange, error, isRegister }) {
  const [visible, setVisible] = useState(false)
  return <div className="auth-field">
    <label htmlFor={name}>{label}</label>
    <div className="password-input"><input id={name} name={name} type={visible ? 'text' : 'password'} value={value} onChange={onChange} autoComplete={isRegister ? 'new-password' : 'current-password'} maxLength={128} required aria-invalid={!!error} aria-describedby={error ? `${name}-error` : isRegister ? 'password-help' : undefined} /><button type="button" aria-label={`${visible ? 'Ocultar' : 'Mostrar'} ${label.toLowerCase()}`} aria-pressed={visible} onClick={() => setVisible(!visible)}>{visible ? 'Ocultar' : 'Ver'}</button></div>
    {error && <p id={`${name}-error`} className="field-error">{error}</p>}
  </div>
}

export default function AuthPage({ kind }) {
  const isRegister = kind === 'register'
  const { status, authenticate } = useAuth()
  const navigate = useNavigate()
  const { state } = useLocation()
  const [values, setValues] = useState({ full_name: '', email: '', password: '', confirmation: '' })
  const [errors, setErrors] = useState({})
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const title = isRegister ? 'Crea tu cuenta' : 'Inicia sesión en tu cuenta'
  useEffect(() => { document.title = `${title} · Splitly`; window.scrollTo(0, 0) }, [title])
  function onChange(event) {
    const { name, value } = event.target
    setValues(previous => ({ ...previous, [name]: value }))
    setErrors(previous => ({ ...previous, [name]: '' }))
    setError('')
  }
  async function submit(event) {
    event.preventDefault()
    if (loading) return
    const form = event.currentTarget
    const invalid = {}
    if (isRegister && !values.full_name.trim()) invalid.full_name = 'Escribe tu nombre completo.'
    if (!values.email.trim() || !form.elements.email.validity.valid) invalid.email = 'Escribe un correo electrónico válido.'
    if (!values.password) invalid.password = 'Escribe tu contraseña.'
    else if (isRegister && values.password.length < 15) invalid.password = 'Usa al menos 15 caracteres.'
    if (isRegister && values.password !== values.confirmation) invalid.confirmation = 'Las contraseñas no coinciden.'
    setErrors(invalid)
    if (Object.keys(invalid).length) { form.elements[Object.keys(invalid)[0]].focus(); return }
    setLoading(true); setError('')
    try {
      const payload = { email: values.email.trim(), password: values.password }
      if (isRegister) payload.full_name = values.full_name.trim()
      await authenticate(kind, payload)
      navigate('/dashboard', { replace: true, state: { notice: isRegister ? 'Tu cuenta está lista. Bienvenido a Splitly.' : 'Sesión iniciada correctamente.' } })
    } catch (failure) { setError(failure.message); setLoading(false) }
  }
  if (status === 'loading' || status === 'error') return <AuthStatus />
  if (status === 'authenticated') return <Navigate to="/dashboard" replace />
  return <main id="contenido" className="shell auth-page"><div className="auth-layout">
    <aside className="auth-story"><Link className="eyebrow auth-back" to="/">← Volver al inicio</Link><p className="eyebrow text-lavender">Splitly / Colombia</p><h1>{isRegister ? <>Los buenos <span>planes</span> empiezan aquí.</> : <>Qué bueno verte <span>de nuevo.</span></>}</h1><p>{isRegister ? 'Un lugar para organizar los grupos y las personas con quienes compartes tus planes.' : 'Tus planes tienen su espacio. Entra para volver a tus grupos.'}</p><div className="auth-manifesto"><span className="eyebrow text-lime">01 / Menos cuentas pendientes</span><p>Más planes juntos.<br />Más tiempo para lo que importa.</p></div><span className="eyebrow auth-prototype">Prototipo / Usa solo datos ficticios</span></aside>
    <section className="auth-form-panel" aria-labelledby="auth-heading"><span className="eyebrow auth-badge">{isRegister ? 'Nuevo usuario / 01' : 'Splitly acceso'}</span><h2 id="auth-heading">{title}</h2><p>{isRegister ? 'Empieza por lo esencial. El próximo plan lo pones tú.' : 'Ingresa tu correo y contraseña para continuar.'}</p>
      {state?.notice && <p role="status">{state.notice}</p>}
      <form onSubmit={submit} noValidate aria-busy={loading}>
        {isRegister && <div className="auth-field"><label htmlFor="full_name">Nombre completo</label><input id="full_name" name="full_name" value={values.full_name} onChange={onChange} autoComplete="name" maxLength={120} required aria-invalid={!!errors.full_name} aria-describedby={errors.full_name ? 'full_name-error' : undefined} />{errors.full_name && <p id="full_name-error" className="field-error">{errors.full_name}</p>}</div>}
        <div className="auth-field"><label htmlFor="email">Correo electrónico</label><input id="email" name="email" type="email" value={values.email} onChange={onChange} autoComplete="email" autoCapitalize="none" spellCheck={false} maxLength={320} required aria-invalid={!!errors.email} aria-describedby={errors.email ? 'email-error' : undefined} />{errors.email && <p id="email-error" className="field-error">{errors.email}</p>}</div>
        <PasswordField name="password" label="Contraseña" value={values.password} onChange={onChange} error={errors.password} isRegister={isRegister} />
        {isRegister && <><p id="password-help" className="auth-help">Entre 15 y 128 caracteres. Puedes usar una frase larga y única.</p><PasswordField name="confirmation" label="Confirmar contraseña" value={values.confirmation} onChange={onChange} error={errors.confirmation} isRegister /></>}
        {error && <p className="form-error" role="alert">{error}</p>}
        <button className="action action-primary auth-submit" type="submit" disabled={loading}>{loading ? 'Un momento…' : isRegister ? 'Crear mi cuenta' : 'Iniciar sesión'}{!loading && <Arrow />}</button>
        {loading && <p role="status" className="auth-help">{isRegister ? 'Creando tu cuenta…' : 'Iniciando sesión…'}</p>}
      </form><p className="auth-switch">{isRegister ? '¿Ya tienes cuenta?' : '¿Aún no tienes cuenta?'} <Link to={isRegister ? '/login' : '/register'}>{isRegister ? 'Inicia sesión' : 'Regístrate aquí'} ↗</Link></p>
    </section></div></main>
}
