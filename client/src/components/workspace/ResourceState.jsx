import { Link } from 'react-router-dom'
import { managementError } from '../../services/groups'

export default function ResourceState({ status, error, onRetry, label = 'tus grupos', children }) {
  if (status === 'loading') return <div className="resource-state" role="status"><span className="eyebrow text-lime">Un momento</span><p>Cargando {label}…</p></div>
  if (status === 'error') return <div className="resource-state"><p role="alert" className="form-error">{error.status === 422 ? 'El identificador del grupo no es válido. Vuelve a mis grupos.' : managementError(error)}</p>{[404, 422].includes(error.status) ? <Link className="action action-secondary" to="/groups">Volver a mis grupos</Link> : <button className="action action-secondary" onClick={onRetry}>Reintentar</button>}</div>
  return children
}
