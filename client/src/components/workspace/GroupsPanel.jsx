import { useState } from 'react'
import { Link } from 'react-router-dom'
import useRemoteResource from '../../hooks/useRemoteResource'
import { groupsService } from '../../services/groups'
import GroupCard from './GroupCard'
import ActionDialog from './ActionDialog'
import ResourceState from './ResourceState'

const normalize = value => value.normalize('NFD').replace(/[\u0300-\u036f]/g, '').toLocaleLowerCase('es')
export default function GroupsPanel({ preview = false }) {
  const resource = useRemoteResource(groupsService.list)
  const [query, setQuery] = useState('')
  const [action, setAction] = useState(null)
  const [notice, setNotice] = useState('')
  const groups = resource.data || []
  const matching = groups.filter(group => normalize(group.name).includes(normalize(query.trim())))
  const visible = preview ? matching.slice(-3).reverse() : matching
  async function submit(name) {
    if (action.kind === 'create') {
      const group = await groupsService.create(name)
      resource.setData(previous => [...previous, group]); setQuery(''); setNotice(`Grupo «${group.name}» creado.`)
    } else if (action.kind === 'edit') {
      const group = await groupsService.update(action.record.id, name)
      resource.setData(previous => previous.map(item => item.id === group.id ? group : item)); setNotice('Nombre del grupo actualizado.')
    } else {
      await groupsService.remove(action.record.id)
      resource.setData(previous => previous.filter(item => item.id !== action.record.id)); setNotice('Grupo eliminado.')
    }
  }
  return <section className="groups-panel" aria-labelledby="groups-heading"><div className="groups-toolbar"><div><h2 id="groups-heading">{preview ? 'Mis grupos' : 'Todos mis grupos'}{resource.status === 'success' && <span className="group-count">{groups.length}</span>}</h2>{!preview && <label className="group-search"><span className="eyebrow">Buscar por nombre</span><input type="search" value={query} onChange={event => setQuery(event.target.value)} placeholder="Tu próximo viaje, la casa…" /></label>}</div><div className="toolbar-actions">{resource.status === 'success' && <button className="workspace-text-button" onClick={() => { setNotice(''); resource.reload() }}>Actualizar</button>}<button className="action action-primary" disabled={resource.status !== 'success'} onClick={() => { setNotice(''); setAction({ kind: 'create' }) }}>Crear grupo <span aria-hidden="true">＋</span></button></div></div>
    {notice && <p role="status" className="workspace-success">{notice}</p>}<ResourceState {...resource} onRetry={resource.reload}>
      {groups.length === 0 ? <div className="workspace-empty"><span className="text-lavender" aria-hidden="true">↗</span><h3>El próximo plan empieza aquí.</h3><p>Aún no tienes grupos. Crea uno y reúne a las personas que compartirán el plan.</p></div> : matching.length === 0 ? <div className="workspace-empty"><h3>No encontramos grupos con ese nombre.</h3><button className="workspace-text-button" onClick={() => setQuery('')}>Limpiar búsqueda</button></div> : <div className="groups-grid">{visible.map((group, index) => <GroupCard key={group.id} group={group} index={index} onEdit={preview ? undefined : record => { setNotice(''); setAction({ kind: 'edit', record }) }} onDelete={record => { setNotice(''); setAction({ kind: 'delete', record }) }} />)}</div>}
      {preview && <Link className="groups-see-all" to="/groups">Ver todos mis grupos <span aria-hidden="true">↗</span></Link>}
    </ResourceState>{action && <ActionDialog key={`${action.kind}-${action.record?.id || 'new'}`} action={action} onSubmit={submit} onClose={() => setAction(null)} />}</section>
}
