import { useCallback, useState } from 'react'
import useRemoteResource from '../../hooks/useRemoteResource'
import { expenseError, expensesService } from '../../services/expenses'
import { createdDate } from '../../utils/format'
import { formatCOP } from '../../utils/money'
import ExpenseDialog from './ExpenseDialog'

export default function GroupFinances({ groupId, members }) {
  const load = useCallback(async signal => {
    const [expenses, balances] = await Promise.all([expensesService.list(groupId, signal), expensesService.balances(groupId, signal)])
    return { expenses, balances }
  }, [groupId])
  const resource = useRemoteResource(load)
  const [action, setAction] = useState(null)
  const [notice, setNotice] = useState('')
  const { expenses = [], balances } = resource.data || {}
  const memberName = id => members.find(member => member.id === id)?.name || 'Participante'

  async function submit(payload) {
    if (action.kind === 'delete') await expensesService.remove(groupId, action.record.id)
    else if (action.kind === 'edit') await expensesService.update(groupId, action.record.id, payload)
    else await expensesService.create(groupId, payload)
    setNotice(action.kind === 'delete' ? 'Gasto eliminado.' : 'Gasto guardado.')
    resource.reload()
  }
  function open(kind, record) { setNotice(''); setAction({ kind, record }) }
  return <section className="group-finances" aria-labelledby="expenses-heading">
    <div className="members-heading"><div><p className="eyebrow text-lavender">Las cuentas de este plan</p><h2 id="expenses-heading">Gastos compartidos</h2></div><div className="toolbar-actions"><button className="workspace-text-button" onClick={() => { setNotice(''); resource.reload() }}>Actualizar gastos y balances</button><button className="action action-primary" disabled={members.length === 0 || resource.status !== 'success'} onClick={() => open('create')}>Añadir gasto <span aria-hidden="true">＋</span></button></div></div>
    {members.length === 0 && <p className="workspace-help">Añade participantes al grupo para registrar el primer gasto.</p>}
    {notice && <p role="status" className="workspace-success">{notice}</p>}
    {resource.status === 'loading' && <p role="status" className="resource-state">Cargando gastos y balances…</p>}
    {resource.status === 'error' && <div className="resource-state"><p role="alert">{expenseError(resource.error)}</p><button className="action action-secondary" onClick={resource.reload}>Reintentar gastos y balances</button></div>}
    {resource.status === 'success' && <>
      <div className="finance-metrics"><article><span className="eyebrow">Total compartido</span><strong>{formatCOP(balances.total_amount)}</strong></article><article><span className="eyebrow">Gastos registrados</span><strong>{balances.expense_count}</strong></article><article className="finance-metric-light"><span className="eyebrow">Participantes del grupo</span><strong>{members.length}</strong><span>Reparto según cada gasto</span></article></div>
      <div className="finances-grid"><div>{expenses.length ? <ul className="expense-list">{[...expenses].reverse().map(expense => <li key={expense.id}><article className="expense-card"><div className="expense-card-title"><div><h3>{expense.description}</h3><p>Pagó {memberName(expense.paid_by)} · <time dateTime={expense.created_at}>{createdDate(expense.created_at)}</time></p></div><strong>{formatCOP(expense.amount)}</strong></div><details><summary>Ver reparto · {expense.shares.length} {expense.shares.length === 1 ? 'persona' : 'personas'}</summary><ul>{expense.shares.map(share => <li key={share.member_id}><span>{memberName(share.member_id)}</span><strong>{formatCOP(share.amount_owed)}</strong></li>)}</ul></details><div className="expense-card-actions"><button className="workspace-text-button" aria-label={`Editar gasto ${expense.description}`} onClick={() => open('edit', expense)}>Editar</button><button className="workspace-text-button danger-text" aria-label={`Eliminar gasto ${expense.description}`} onClick={() => open('delete', expense)}>Eliminar</button></div></article></li>)}</ul> : <div className="workspace-empty"><h3>Aún no hay gastos.</h3><p>Registra el primer gasto de este plan para ver el reparto y las deudas.</p></div>}</div>
        <aside className="transfers-panel" aria-labelledby="transfers-heading"><p className="eyebrow text-lavender">Emparejamiento determinista</p><h2 id="transfers-heading">Transferencias sugeridas</h2><p>Orientación para saldar las cuentas. No realiza pagos ni garantiza la menor cantidad global de transferencias.</p>{balances.transfers.length ? <ul>{balances.transfers.map(transfer => <li key={`${transfer.from_member_id}-${transfer.to_member_id}`}><span>{memberName(transfer.from_member_id)} debe <strong>{formatCOP(transfer.amount)}</strong> a {memberName(transfer.to_member_id)}</span></li>)}</ul> : <p className="transfers-empty">No hay transferencias pendientes según los gastos registrados.</p>}</aside></div>
      <section className="balances-section" aria-labelledby="balances-heading"><div className="members-heading"><h2 id="balances-heading">Balances por participante</h2><span className="eyebrow text-lime">Pagado − parte correspondiente = saldo neto</span></div>{balances.members.length ? <div className="balance-table-scroll" tabIndex={0} role="region" aria-label="Tabla de balances con desplazamiento horizontal"><table className="balance-table"><caption>Importes en COP. Positivo: recibe. Negativo: paga.</caption><thead><tr><th scope="col">Participante</th><th scope="col">Total pagado</th><th scope="col">Le corresponde</th><th scope="col">Saldo neto</th></tr></thead><tbody>{balances.members.map(member => <tr key={member.member_id}><th scope="row">{member.name}</th><td>{formatCOP(member.total_paid)}</td><td>{formatCOP(member.total_owed)}</td><td className={member.net_balance > 0 ? 'text-lime' : member.net_balance < 0 ? 'text-lavender' : ''}>{member.net_balance > 0 ? '+' : ''}{formatCOP(member.net_balance)}<span className="balance-direction">{member.net_balance > 0 ? 'Debe recibir' : member.net_balance < 0 ? 'Debe pagar' : 'En equilibrio'}</span></td></tr>)}</tbody></table></div> : <p>Añade participantes para ver sus balances.</p>}</section>
    </>}
    {action && <ExpenseDialog key={`${action.kind}-${action.record?.id || 'new'}`} action={action} members={members} onSubmit={submit} onClose={() => setAction(null)} />}
  </section>
}
