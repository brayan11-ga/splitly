from uuid import UUID

from sqlmodel import Session

from app.db import repositories
from app.models import Member
from app.services.errors import NotFoundError, commit
from app.services.groups import get_group


def get_member(session: Session, group_id: UUID, member_id: UUID, owner_id: UUID) -> Member:
    get_group(session, group_id, owner_id)
    member = repositories.find_member(session, group_id, member_id)
    if member is None:
        raise NotFoundError("Participante no encontrado en el grupo indicado.")
    return member


def list_members(session: Session, group_id: UUID, owner_id: UUID) -> list[Member]:
    get_group(session, group_id, owner_id)
    return repositories.list_members(session, group_id)


def create_member(session: Session, group_id: UUID, name: str, owner_id: UUID) -> Member:
    get_group(session, group_id, owner_id)
    member = Member(group_id=group_id, name=name)
    session.add(member)
    commit(session)
    session.refresh(member)
    return member


def update_member(session: Session, group_id: UUID, member_id: UUID, name: str, owner_id: UUID) -> Member:
    member = get_member(session, group_id, member_id, owner_id)
    member.name = name
    session.add(member)
    commit(session)
    session.refresh(member)
    return member


def delete_member(session: Session, group_id: UUID, member_id: UUID, owner_id: UUID) -> None:
    member = get_member(session, group_id, member_id, owner_id)
    session.delete(member)
    commit(session)
