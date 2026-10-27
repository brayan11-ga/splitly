import { useEffect, useId, useRef, useState } from 'react'
import { createPortal } from 'react-dom'
import { motion, useReducedMotion } from 'motion/react'
import { expenseError } from '../../services/expenses'
import { formatCOP, MAX_COP, parseCOP, previewShares } from '../../utils/money'

export default function ExpenseDialog({ action, members, onSubmit, onClose }) {
  const dialog = useRef(null)
  const descriptionInput = useRef(null)
  const id = useId()
  const reduced = useReducedMotion()
  const removing = action.kind === 'delete'
  const record = action.record
  const [description, setDescription] = useState(record?.description || '')
  const [amount, setAmount] = useState(record ? String(record.amount) : '')
  const [paidBy, setPaidBy] = useState(record?.paid_by || members[0]?.id || '')
  const [selected, setSelected] = useState(record ? record.shares.map(share => share.member_id) : members.map(member => member.id))
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState('')
  const parsed = parseCOP(amount)
  const preview = previewShares(parsed, members.filter(member => selected.includes(member.id)))
  const title = removing ? 'Eliminar gasto' : action.kind === 'edit' ? 'Editar gasto' : 'Añadir gasto'

  useEffect(() => {
    const node = dialog.current
    const trigger = document.activeElement
    node.showModal()
    descriptionInput.current?.focus()
    return () => {
      node.close()
      if (trigger?.isConnected) trigger.focus()
      else document.querySelector('[data-page-heading]')?.focus()
    }
  }, [])

  function toggle(memberId) {
    setSelected(previous => previous.includes(memberId) ? previous.filter(value => value !== memberId) : [...previous, memberId])
  }
  async function submit(event) {
    event.preventDefault()
    if (busy) return
    if (!removing && (!description.trim() || description.trim().length > 240 || !parsed || !paidBy || selected.length === 0)) {
      setError('Completa la descripción, un importe entero positivo en COP, el pagador y al menos un participante.')
      return
    }
    setError(''); setBusy(true)
    try {
      await onSubmit({ description: description.trim(), amount: parsed, paid_by: paidBy, participant_ids: selected })
      onClose()
    } catch (failure) { setError(expenseError(failure)); setBusy(false) }
  }
  return createPortal(
    <dialog ref={dialog} className="workspace-dialog expense-dialog" aria-labelledby={id + '-title'} aria-describedby={id + '-help'}
      onCancel={event => { event.preventDefault(); if (!busy) onClose() }}
      onClick={event => { if (event.target === event.currentTarget && !busy) onClose() }}>
      <motion.div className="workspace-dialog-content" initial={reduced ? false : { opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: reduced ? 0 : .15 }}>
        <div className="dialog-heading"><p className="eyebrow text-lime">Splitly / Pesos colombianos</p><button type="button" className="dialog-close" aria-label="Cerrar diálogo" disabled={busy} onClick={onClose}>×</button></div>
        <h2 id={id + '-title'}>{title}</h2>
        <p id={id + '-help'}>{removing ? <>¿Eliminar <strong>{record.description}</strong> por {formatCOP(record.amount)}? También se eliminará su reparto y se recalcularán los balances. Esta acción no se puede deshacer.</> : 'Reparto equitativo en pesos enteros. El pagador puede estar incluido o no entre los participantes.'}</p>
        <form onSubmit={submit} noValidate aria-busy={busy}>
          {!removing && <fieldset disabled={busy} className="expense-fields">
            <div className="workspace-field"><label htmlFor={id + '-description'}>Descripción del gasto</label><input ref={descriptionInput} id={id + '-description'} value={description} onChange={event => setDescription(event.target.value)} maxLength={240} required autoComplete="off" /></div>
            <div className="expense-field-row"><div className="workspace-field"><label htmlFor={id + '-amount'}>Importe en COP</label><input id={id + '-amount'} type="text" inputMode="numeric" value={amount} onChange={event => setAmount(event.target.value)} required aria-describedby={id + '-amount-help'} /><p id={id + '-amount-help'} className="workspace-help">Sin puntos ni decimales. Ejemplo: 90000. Máximo {formatCOP(MAX_COP)}.</p></div>
              <div className="workspace-field"><label htmlFor={id + '-payer'}>Pagó</label><select id={id + '-payer'} value={paidBy} onChange={event => setPaidBy(event.target.value)} required>{members.map(member => <option key={member.id} value={member.id}>{member.name}</option>)}</select></div></div>
            <fieldset className="expense-participants"><legend>Participantes del reparto</legend><p className="workspace-help">Selecciona al menos una persona.</p><div className="participant-checkboxes">{members.map(member => <label key={member.id}><input type="checkbox" checked={selected.includes(member.id)} onChange={() => toggle(member.id)} />{member.name}</label>)}</div></fieldset>
            <section className="expense-preview" aria-label="Vista previa del reparto"><h3>Vista previa del reparto</h3><p className="workspace-help">Si hay pesos sobrantes, algunas personas asumen un peso adicional. El orden de asignación es estable.</p>{preview.length ? <ul>{preview.map(share => <li key={share.id}><span>{share.name}</span><strong>{formatCOP(share.amount_owed)}</strong></li>)}</ul> : <p>Introduce un importe válido y selecciona participantes.</p>}</section>
          </fieldset>}
          {error && <p role="alert" className="form-error">{error}</p>}
          <div className="dialog-actions"><button type="button" className="action action-secondary" disabled={busy} onClick={onClose}>Cancelar</button><button type="submit" className={`action ${removing ? 'action-danger' : 'action-primary'}`} disabled={busy}>{busy ? 'Guardando…' : removing ? 'Eliminar gasto' : action.kind === 'edit' ? 'Guardar gasto' : 'Crear gasto'}</button></div>
        </form>
      </motion.div>
    </dialog>, document.body,
  )
}
