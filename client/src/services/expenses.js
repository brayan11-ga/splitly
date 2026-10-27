import { apiRequest } from './api'

const base = groupId => `/groups/${encodeURIComponent(groupId)}`
export const expensesService = {
  list: (groupId, signal) => apiRequest(`${base(groupId)}/expenses`, { signal }),
  get: (groupId, id, signal) => apiRequest(`${base(groupId)}/expenses/${encodeURIComponent(id)}`, { signal }),
  create: (groupId, body) => apiRequest(`${base(groupId)}/expenses`, { method: 'POST', body }),
  update: (groupId, id, body) => apiRequest(`${base(groupId)}/expenses/${encodeURIComponent(id)}`, { method: 'PATCH', body }),
  remove: (groupId, id) => apiRequest(`${base(groupId)}/expenses/${encodeURIComponent(id)}`, { method: 'DELETE' }),
  balances: (groupId, signal) => apiRequest(`${base(groupId)}/balances`, { signal }),
}

export function expenseError(error) {
  if (error.status === 409) return 'El gasto tiene un conflicto con los participantes. Actualiza el grupo y revisa la selección.'
  if (error.status === 404) return 'El gasto o el grupo ya no está disponible. Actualiza la página.'
  if (error.status === 422) return 'Revisa el importe entero en COP, la descripción y los participantes de este grupo. El total debe estar dentro del límite admitido.'
  return error.message
}
