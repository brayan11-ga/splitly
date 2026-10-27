from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, StringConstraints, field_validator


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    email: EmailStr
    password: Annotated[str, StringConstraints(strict=True, min_length=1, max_length=128)] = Field(repr=False)

    @field_validator("email", mode="before")
    @classmethod
    def normalize_email(cls, value):
        return value.strip().lower() if isinstance(value, str) else value


class RegisterRequest(LoginRequest):
    full_name: Annotated[str, StringConstraints(strict=True, strip_whitespace=True, min_length=1, max_length=120)]
    password: Annotated[str, StringConstraints(strict=True, min_length=15, max_length=128)] = Field(repr=False)


class UserRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    full_name: str
    email: str
    created_at: datetime


class AuthResponse(BaseModel):
    user: UserRead
    csrf_token: str
