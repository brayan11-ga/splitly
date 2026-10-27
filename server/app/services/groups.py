from uuid import UUID

from sqlmodel import Session

from app.db import repositories
from app.models import Group
from app.services.errors import ConflictError, NotFoundError, commit


def get_group(session: Session, group_id: UUID, owner_id: UUID, lock: bool = False) -> Group:
    """Punto de autorización reutilizable también para futuros gastos."""
    group = repositories.find_group(session, group_id, owner_id, lock=lock)
    if group is None:
        raise NotFoundError("Grupo no encontrado.")
    return group


def list_groups(session: Session, owner_id: UUID) -> list[Group]:
    return repositories.list_groups(session, owner_id)


def create_group(session: Session, name: str, owner_id: UUID) -> Group:
    group = Group(name=name, owner_id=owner_id)
    session.add(group)
    commit(session)
    session.refresh(group)
    return group


def update_group(session: Session, group_id: UUID, name: str, owner_id: UUID) -> Group:
    group = get_group(session, group_id, owner_id)
    group.name = name
    session.add(group)
    commit(session)
    session.refresh(group)
    return group


def delete_group(session: Session, group_id: UUID, owner_id: UUID) -> None:
    group = get_group(session, group_id, owner_id)
    if repositories.has_members(session, group_id):
        raise ConflictError("Elimina los participantes antes de eliminar el grupo.")
    session.delete(group)
    commit(session)
