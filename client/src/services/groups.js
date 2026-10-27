import { apiRequest } from './api'

const groupPath = id => `/groups/${encodeURIComponent(id)}`
const membersPath = id => `${groupPath(id)}/members`
export const groupsService = {
  list: signal => apiRequest('/groups', { signal }),
  get: (id, signal) => apiRequest(groupPath(id), { signal }),
  create: name => apiRequest('/groups', { method: 'POST', body: { name } }),
  update: (id, name) => apiRequest(groupPath(id), { method: 'PATCH', body: { name } }),
  remove: id => apiRequest(groupPath(id), { method: 'DELETE' }),
  listMembers: (groupId, signal) => apiRequest(membersPath(groupId), { signal }),
  createMember: (groupId, name) => apiRequest(membersPath(groupId), { method: 'POST', body: { name } }),
  updateMember: (groupId, id, name) => apiRequest(`${membersPath(groupId)}/${encodeURIComponent(id)}`, { method: 'PATCH', body: { name } }),
  removeMember: (groupId, id) => apiRequest(`${membersPath(groupId)}/${encodeURIComponent(id)}`, { method: 'DELETE' }),
}
export function managementError(error, entity = 'group', action) {
  if (error.status === 404) return entity === 'group' ? 'Este grupo ya no está disponible o no tienes acceso a él.' : 'Este participante ya no está disponible en el grupo. Actualiza la página.'
  if (error.status === 409 && entity === 'group' && action === 'delete') return 'El grupo tiene participantes. Elimínalos desde el detalle antes de borrar el grupo.'
  if (error.status === 422) return 'Escribe un nombre válido. No puede estar vacío ni contener solo espacios.'
  return error.message
}
