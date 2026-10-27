import { motion, useReducedMotion } from 'motion/react'
import { Link } from 'react-router-dom'
import { Arrow } from '../LandingUI'
import { createdDate } from '../../utils/format'
export default function GroupCard({ group, index, onEdit, onDelete }) {
  const reduced = useReducedMotion()
  return <motion.article className={`group-card group-card-${index % 3}`} initial={reduced ? false : { opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: reduced ? 0 : .2, delay: reduced ? 0 : Math.min(index * .025, .15) }}>
    <div className="group-card-top"><span className="eyebrow">Grupo personal</span><span className="eyebrow">{String(index + 1).padStart(2, '0')} / COP</span></div><div className="group-monogram" aria-hidden="true">{Array.from(group.name)[0]?.toLocaleUpperCase('es')}</div>
    <h3><Link to={`/groups/${group.id}`}>{group.name}</Link></h3><p className="group-created">Creado el <time dateTime={group.created_at}>{createdDate(group.created_at)}</time></p>
    <Link className="group-enter" to={`/groups/${group.id}`} aria-label={`Ver grupo ${group.name}`}>Entrar al grupo <Arrow /></Link>
    {onEdit && <div className="group-card-actions"><button onClick={() => onEdit(group)} aria-label={`Editar grupo ${group.name}`}>Editar nombre</button><button onClick={() => onDelete(group)} aria-label={`Eliminar grupo ${group.name}`}>Eliminar</button></div>}
  </motion.article>
}
