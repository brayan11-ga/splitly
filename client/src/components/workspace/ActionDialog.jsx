import { useEffect, useId, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { Link } from 'react-router-dom'
import { motion, useReducedMotion } from 'motion/react'
import { managementError } from '../../services/groups'

export default function ActionDialog({ action, entity = 'group', onSubmit, onClose }) {
  const dialog = useRef(null)
  const input = useRef(null)
  const titleId = useId()
  const descriptionId = useId()
  const errorId = useId()
  const reduced = useReducedMotion()
  const [name, setName] = useState(action.record?.name || '')
  const [busy, setBusy] = useState(false)
  const [fieldError, setFieldError] = useState('')
  const [error, setError] = useState(null)
  const removing = action.kind === 'delete'
  const noun = entity === 'group' ? 'grupo' : 'participante'
  const title = `${removing ? 'Eliminar' : action.kind === 'edit' ? 'Editar' : 'Crear'} ${noun}`
  useEffect(() => {
    const node = dialog.current
    const trigger = document.activeElement
    node.showModal()
    if (input.current) { input.current.focus(); input.current.select() }
    return () => { node.close(); if (trigger?.isConnected) trigger.focus(); else document.querySelector('[data-page-heading]')?.focus() }
  }, [])
  async function submit(event) {
    event.preventDefault()
    if (busy) return
    if (!removing && !name.trim()) { setFieldError('Escribe un nombre. No puede contener solo espacios.'); input.current.focus(); return }
    setBusy(true); setError(null); setFieldError('')
    try { await onSubmit(name.trim()); onClose() }
    catch (failure) { setError(failure); setBusy(false) }
  }
  return createPortal(<dialog ref={dialog} className="workspace-dialog" aria-labelledby={titleId} aria-describedby={descriptionId} onCancel={event => { event.preventDefault(); if (!busy) onClose() }} onClick={event => { if (event.target === event.currentTarget && !busy) onClose() }}><motion.div className="workspace-dialog-content" initial={reduced ? false : { opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: reduced ? 0 : .15 }}>
    <div className="dialog-heading"><p className="eyebrow text-lime">Splitly / {removing ? 'Confirmar acción' : 'Tu próximo plan'}</p><button type="button" className="dialog-close" aria-label="Cerrar diálogo" onClick={onClose} disabled={busy}>×</button></div><h2 id={titleId}>{title}</h2>
    <p id={descriptionId}>{removing ? <>¿Quieres eliminar a <strong>{action.record.name}</strong>? Esta acción no se puede deshacer.{entity === 'group' && ' El grupo debe estar sin participantes.'}</> : entity === 'group' ? 'Solo necesitas un nombre. Podrás añadir participantes desde el detalle.' : 'Añade el nombre de la persona que compartirá este plan.'}</p>
    <form onSubmit={submit} noValidate aria-busy={busy}>{!removing && <div className="workspace-field"><label htmlFor={titleId + '-name'}>Nombre del {noun}</label><input ref={input} id={titleId + '-name'} name="name" value={name} onChange={event => { setName(event.target.value); setFieldError(''); setError(null) }} autoComplete="off" required aria-invalid={!!fieldError} aria-describedby={fieldError ? errorId : undefined} />{fieldError && <p id={errorId} className="field-error">{fieldError}</p>}</div>}
      {error && <div><p role="alert" className="form-error">{managementError(error, entity, action.kind)}</p>{entity === 'group' && removing && error.status === 409 && <Link className="dialog-detail-link" to={`/groups/${action.record.id}`} onClick={onClose}>Gestionar participantes →</Link>}</div>}
      <div className="dialog-actions"><button type="button" className="action action-secondary" disabled={busy} onClick={onClose}>Cancelar</button><button className={`action ${removing ? 'action-danger' : 'action-primary'}`} type="submit" disabled={busy}>{busy ? 'Guardando…' : removing ? `Eliminar ${noun}` : action.kind === 'edit' ? 'Guardar cambios' : `Crear ${noun}`}</button></div>{busy && <p role="status" className="workspace-help">{removing ? 'Eliminando registro…' : 'Guardando cambios…'}</p>}
    </form></motion.div></dialog>, document.body)
}
