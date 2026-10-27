from uuid import UUID

from app.schemas.groups import GroupRead, NameRequest


class MemberCreate(NameRequest):
    pass


class MemberUpdate(NameRequest):
    pass


class MemberRead(GroupRead):
    group_id: UUID
