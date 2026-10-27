from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, SQLModel


class AuthSession(SQLModel, table=True):
    __tablename__ = "auth_sessions"

    token_hash: str = Field(max_length=64, primary_key=True, repr=False)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    expires_at: datetime = Field(sa_column=Column(DateTime(timezone=True), nullable=False, index=True))
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False, server_default=func.now()),
    )
