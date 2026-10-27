from uuid import UUID

from sqlmodel import Session

from app.db import repositories
from app.models import Group
from app.services.errors import ConflictError, NotFoundError, commit


def get_group(session: Session, group_id: UUID) -> Group:
    group = repositories.find_group(session, group_id)
    if group is None:
        raise NotFoundError("Grupo no encontrado.")
    return group


def list_groups(session: Session) -> list[Group]:
    return repositories.list_groups(session)


def create_group(session: Session, name: str) -> Group:
    group = Group(name=name)
    session.add(group)
    commit(session)
    session.refresh(group)
    return group


def update_group(session: Session, group_id: UUID, name: str) -> Group:
    group = get_group(session, group_id)
    group.name = name
    session.add(group)
    commit(session)
    session.refresh(group)
    return group


def delete_group(session: Session, group_id: UUID) -> None:
    group = get_group(session, group_id)
    if repositories.has_members(session, group_id):
        raise ConflictError("Elimina los participantes antes de eliminar el grupo.")
    session.delete(group)
    commit(session)
