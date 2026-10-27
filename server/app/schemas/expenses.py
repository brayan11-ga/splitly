from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, model_validator

from app.services.money import MAX_AMOUNT

Description = Annotated[str, StringConstraints(strict=True, strip_whitespace=True, min_length=1, max_length=240)]
Amount = Annotated[int, Field(strict=True, gt=0, le=MAX_AMOUNT)]
Participants = Annotated[list[UUID], Field(min_length=1, max_length=1000)]


class ExpenseCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    description: Description
    amount: Amount
    paid_by: UUID
    participant_ids: Participants

    @model_validator(mode="after")
    def unique_participants(self):
        if len(set(self.participant_ids)) != len(self.participant_ids):
            raise ValueError("No se permiten participantes repetidos.")
        return self


class ExpenseUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")
    description: Description | None = None
    amount: Amount | None = None
    paid_by: UUID | None = None
    participant_ids: Participants | None = None

    @model_validator(mode="after")
    def validate_update(self):
        if not self.model_fields_set or any(getattr(self, name) is None for name in self.model_fields_set):
            raise ValueError("Envía al menos un campo y no uses null.")
        if self.participant_ids is not None and len(set(self.participant_ids)) != len(self.participant_ids):
            raise ValueError("No se permiten participantes repetidos.")
        return self


class ShareRead(BaseModel):
    member_id: UUID
    amount_owed: int


class ExpenseRead(BaseModel):
    id: UUID
    group_id: UUID
    paid_by: UUID
    description: str
    amount: int
    created_at: datetime
    shares: list[ShareRead]


class MemberBalance(BaseModel):
    member_id: UUID
    name: str
    total_paid: int
    total_owed: int
    net_balance: int


class TransferRead(BaseModel):
    from_member_id: UUID
    to_member_id: UUID
    amount: int


class BalancesRead(BaseModel):
    group_id: UUID
    total_amount: int
    expense_count: int
    members: list[MemberBalance]
    transfers: list[TransferRead]
