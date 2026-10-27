from uuid import UUID

from fastapi import APIRouter, Response

from app.routers.dependencies import SessionDep
from app.schemas.members import MemberCreate, MemberRead, MemberUpdate
from app.services import members

router = APIRouter(
    prefix="/groups/{group_id}/members", tags=["members"],
    responses={404: {"description": "Grupo o participante no encontrado"}},
)


@router.post("", response_model=MemberRead, status_code=201)
def create_member(group_id: UUID, payload: MemberCreate, session: SessionDep):
    return members.create_member(session, group_id, payload.name)


@router.get("", response_model=list[MemberRead])
def list_members(group_id: UUID, session: SessionDep):
    return members.list_members(session, group_id)


@router.patch("/{member_id}", response_model=MemberRead)
def update_member(group_id: UUID, member_id: UUID, payload: MemberUpdate, session: SessionDep):
    return members.update_member(session, group_id, member_id, payload.name)


@router.delete("/{member_id}", status_code=204)
def delete_member(group_id: UUID, member_id: UUID, session: SessionDep):
    members.delete_member(session, group_id, member_id)
    return Response(status_code=204)
