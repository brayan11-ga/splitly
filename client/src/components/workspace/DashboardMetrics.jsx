import { useCallback } from 'react'
import useRemoteResource from '../../hooks/useRemoteResource'
import { groupsService } from '../../services/groups'
import { expensesService } from '../../services/expenses'
import { formatCOP } from '../../utils/money'

export default function DashboardMetrics() {
  const load = useCallback(async signal => {
    const groups = await groupsService.list(signal)
    const summaries = []
    // Limit concurrent requests for accounts with many groups.
    for (let offset = 0; offset < groups.length; offset += 5) {
      summaries.push(...await Promise.all(groups.slice(offset, offset + 5).map(group => expensesService.balances(group.id, signal))))
    }
    return {
      groups: groups.length,
      expenses: summaries.reduce((sum, summary) => sum + summary.expense_count, 0),
      amount: summaries.reduce((sum, summary) => sum + BigInt(summary.total_amount), 0n),
    }
  }, [])
  const resource = useRemoteResource(load)
  return <section className="dashboard-metrics" aria-label="Métricas reales de tus grupos">
    <div className="members-heading"><p className="eyebrow text-lavender">Resumen de tus grupos · COP</p><button className="workspace-text-button" onClick={resource.reload}>Actualizar métricas</button></div>
    {resource.status === 'loading' && <p role="status">Cargando métricas…</p>}
    {resource.status === 'error' && <p role="alert">No pudimos cargar las métricas. Usa Actualizar métricas para reintentar.</p>}
    {resource.status === 'success' && <div className="finance-metrics"><article><span className="eyebrow">Mis grupos</span><strong>{resource.data.groups}</strong></article><article><span className="eyebrow">Gastos registrados</span><strong>{resource.data.expenses}</strong></article><article className="finance-metric-light"><span className="eyebrow">Total compartido entre tus grupos</span><strong>{formatCOP(resource.data.amount)}</strong><span>Total grupal, no tu saldo personal</span></article></div>}
  </section>
}
