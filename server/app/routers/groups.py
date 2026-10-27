from uuid import UUID

from fastapi import APIRouter, Response

from app.routers.dependencies import SessionDep
from app.schemas.groups import GroupCreate, GroupRead, GroupUpdate
from app.services import groups
from app.routers.auth_dependencies import CurrentUser

router = APIRouter(prefix="/groups", tags=["groups"], responses={404: {"description": "Grupo no encontrado"}})


@router.post("", response_model=GroupRead, status_code=201)
def create_group(payload: GroupCreate, session: SessionDep, user: CurrentUser):
    return groups.create_group(session, payload.name, user.id)


@router.get("", response_model=list[GroupRead])
def list_groups(session: SessionDep, user: CurrentUser):
    return groups.list_groups(session, user.id)


@router.get("/{group_id}", response_model=GroupRead)
def get_group(group_id: UUID, session: SessionDep, user: CurrentUser):
    return groups.get_group(session, group_id, user.id)


@router.patch("/{group_id}", response_model=GroupRead)
def update_group(group_id: UUID, payload: GroupUpdate, session: SessionDep, user: CurrentUser):
    return groups.update_group(session, group_id, payload.name, user.id)


@router.delete("/{group_id}", status_code=204, responses={409: {"description": "El grupo tiene participantes o registros relacionados"}})
def delete_group(group_id: UUID, session: SessionDep, user: CurrentUser):
    groups.delete_group(session, group_id, user.id)
    return Response(status_code=204)
