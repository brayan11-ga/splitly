"""Consultas de persistencia; las transacciones se deciden en servicios."""

from uuid import UUID

from sqlmodel import Session, select

from app.models import Group, Member


def find_group(session: Session, group_id: UUID) -> Group | None:
    return session.get(Group, group_id)


def list_groups(session: Session) -> list[Group]:
    return list(session.exec(select(Group).order_by(Group.created_at, Group.id)).all())


def find_member(session: Session, group_id: UUID, member_id: UUID) -> Member | None:
    return session.exec(select(Member).where(
        Member.id == member_id, Member.group_id == group_id,
    )).first()


def list_members(session: Session, group_id: UUID) -> list[Member]:
    return list(session.exec(select(Member).where(Member.group_id == group_id)
                             .order_by(Member.created_at, Member.id)).all())


def has_members(session: Session, group_id: UUID) -> bool:
    return session.exec(select(Member.id).where(Member.group_id == group_id).limit(1)).first() is not None
