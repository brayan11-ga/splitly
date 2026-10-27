from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, StringConstraints

Name = Annotated[str, StringConstraints(strict=True, strip_whitespace=True, min_length=1)]


class NameRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    name: Name


class GroupCreate(NameRequest):
    pass


class GroupUpdate(NameRequest):
    """El nombre es el único campo editable y debe estar presente."""


class GroupRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    created_at: datetime
