import { useCallback, useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import WorkspaceNav from '../components/workspace/WorkspaceNav'
import ActionDialog from '../components/workspace/ActionDialog'
import ResourceState from '../components/workspace/ResourceState'
import { createdDate } from '../utils/format'
import useRemoteResource from '../hooks/useRemoteResource'
import { groupsService } from '../services/groups'

function GroupDetail({ groupId }) {
  const navigate = useNavigate()
  const load = useCallback(async signal => {
    const [group, members] = await Promise.all([groupsService.get(groupId, signal), groupsService.listMembers(groupId, signal)])
    return { group, members }
  }, [groupId])
  const resource = useRemoteResource(load)
  const [action, setAction] = useState(null)
  const [notice, setNotice] = useState('')
  const { group, members = [] } = resource.data || {}
  useEffect(() => { document.title = `${group?.name || 'Detalle de grupo'} · Splitly` }, [group?.name])
  async function submit(name) {
    if (action.entity === 'group') {
      if (action.kind === 'edit') {
        const updated = await groupsService.update(groupId, name)
        resource.setData(previous => ({ ...previous, group: updated })); setNotice('Nombre del grupo actualizado.')
      } else { await groupsService.remove(groupId); navigate('/groups', { replace: true, state: { notice: 'Grupo eliminado.' } }); return }
    } else if (action.kind === 'create') {
      const member = await groupsService.createMember(groupId, name)
      resource.setData(previous => ({ ...previous, members: [...previous.members, member] })); setNotice(`Participante «${member.name}» creado.`)
    } else if (action.kind === 'edit') {
      const member = await groupsService.updateMember(groupId, action.record.id, name)
      resource.setData(previous => ({ ...previous, members: previous.members.map(item => item.id === member.id ? member : item) })); setNotice('Participante actualizado.')
    } else {
      await groupsService.removeMember(groupId, action.record.id)
      resource.setData(previous => ({ ...previous, members: previous.members.filter(item => item.id !== action.record.id) })); setNotice('Participante eliminado.')
    }
  }
  function open(kind, entity, record) { setNotice(''); setAction({ kind, entity, record }) }
  return <main id="contenido" className="shell workspace-page"><WorkspaceNav /><Link className="workspace-back eyebrow" to="/groups">← Volver a mis grupos</Link><ResourceState {...resource} onRetry={resource.reload} label="el grupo y sus participantes">
    {group && <><header className="workspace-heading detail-heading"><div><p className="eyebrow text-lavender">Mis grupos / Tu plan compartido</p><h1 data-page-heading tabIndex={-1}>{group.name}</h1><p>Creado el <time dateTime={group.created_at}>{createdDate(group.created_at)}</time></p></div><div className="detail-actions"><button className="action action-secondary" onClick={() => open('edit', 'group', group)}>Editar grupo</button><button className="workspace-text-button danger-text" onClick={() => open('delete', 'group', group)}>Eliminar grupo</button></div></header>
      <div className="detail-meta"><span className="eyebrow">{members.length} {members.length === 1 ? 'participante' : 'participantes'}</span><span className="eyebrow">Moneda del proyecto / COP</span><button className="workspace-text-button" onClick={() => { setNotice(''); resource.reload() }}>Actualizar</button></div>{notice && <p role="status" className="workspace-success">{notice}</p>}
      <div className="group-detail-grid"><section className="members-panel" aria-labelledby="members-heading"><div className="members-heading"><h2 id="members-heading">Participantes</h2><button className="action action-primary" onClick={() => open('create', 'member')}>Añadir participante <span aria-hidden="true">＋</span></button></div>
        {members.length ? <ul className="members-list">{members.map((member, index) => <li key={member.id}><span className={`member-avatar member-avatar-${index % 3}`} aria-hidden="true">{Array.from(member.name)[0]?.toLocaleUpperCase('es')}</span><div className="member-name"><h3>{member.name}</h3><p>En este grupo desde {createdDate(member.created_at)}</p></div><div className="member-actions"><button className="workspace-text-button" aria-label={`Editar participante ${member.name}`} onClick={() => open('edit', 'member', member)}>Editar</button><button className="workspace-text-button danger-text" aria-label={`Eliminar participante ${member.name}`} onClick={() => open('delete', 'member', member)}>Eliminar</button></div></li>)}</ul> : <div className="workspace-empty"><h3>Todo plan empieza por su gente.</h3><p>Aún no hay participantes. Añade a la primera persona para organizar el grupo.</p></div>}
      </section><aside className="group-plan-note"><span className="eyebrow text-lavender">El siguiente paso</span><h2>Primero el grupo.<br /><span className="text-lime">Luego las cuentas.</span></h2><p>Ya puedes gestionar a las personas de este plan. El registro de gastos y los balances todavía no están disponibles.</p><span aria-hidden="true">↗</span></aside></div></>}
    </ResourceState>{action && <ActionDialog key={`${action.entity}-${action.kind}-${action.record?.id || 'new'}`} action={action} entity={action.entity} onSubmit={submit} onClose={() => setAction(null)} />}</main>
}
export default function GroupDetailPage() {
  const { groupId } = useParams()
  return <GroupDetail key={groupId} groupId={groupId} />
}
