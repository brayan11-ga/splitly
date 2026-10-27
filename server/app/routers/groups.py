from uuid import UUID

from fastapi import APIRouter, Response

from app.routers.dependencies import SessionDep
from app.schemas.groups import GroupCreate, GroupRead, GroupUpdate
from app.services import groups

router = APIRouter(prefix="/groups", tags=["groups"], responses={404: {"description": "Grupo no encontrado"}})


@router.post("", response_model=GroupRead, status_code=201)
def create_group(payload: GroupCreate, session: SessionDep):
    return groups.create_group(session, payload.name)


@router.get("", response_model=list[GroupRead])
def list_groups(session: SessionDep):
    return groups.list_groups(session)


@router.get("/{group_id}", response_model=GroupRead)
def get_group(group_id: UUID, session: SessionDep):
    return groups.get_group(session, group_id)


@router.patch("/{group_id}", response_model=GroupRead)
def update_group(group_id: UUID, payload: GroupUpdate, session: SessionDep):
    return groups.update_group(session, group_id, payload.name)


@router.delete("/{group_id}", status_code=204, responses={409: {"description": "El grupo tiene participantes o registros relacionados"}})
def delete_group(group_id: UUID, session: SessionDep):
    groups.delete_group(session, group_id)
    return Response(status_code=204)
