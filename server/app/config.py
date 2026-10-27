"""Configuración del servidor; nunca se comparte con Vite."""

import os
from pathlib import Path
from typing import Literal
from urllib.parse import urlsplit

from dotenv import load_dotenv
from pydantic import BaseModel, Field, SecretStr, model_validator


class Settings(BaseModel):
    database_url: SecretStr | None = None
    environment: Literal["development", "production"] = "development"
    cookie_secure: bool = False
    cookie_samesite: Literal["lax", "strict", "none"] = "lax"
    session_ttl_seconds: int = Field(default=28800, ge=60, le=86400)
    csrf_trusted_origins: list[str] = Field(default_factory=list)
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"]
    )

    @property
    def cookie_name(self) -> str:
        return "__Host-splitly_session" if self.environment == "production" else "splitly_session"

    @property
    def trusted_origins(self) -> set[str]:
        origins = set(self.cors_origins + self.csrf_trusted_origins)
        if self.environment == "development":
            origins.update({"http://localhost:8000", "http://127.0.0.1:8000"})
        return origins

    @model_validator(mode="after")
    def validate_security(self):
        if not self.cors_origins:
            raise ValueError("CORS_ORIGINS debe contener orígenes explícitos.")
        for origin in self.trusted_origins:
            parsed = urlsplit(origin)
            if (parsed.scheme not in {"http", "https"} or not parsed.netloc
                    or parsed.path or parsed.query or parsed.fragment or parsed.username
                    or "*" in origin):
                raise ValueError("Los orígenes deben ser URLs exactas sin ruta ni comodines.")
            if self.environment == "production" and parsed.scheme != "https":
                raise ValueError("Producción requiere orígenes HTTPS explícitos.")
        if self.cookie_samesite == "none" and not self.cookie_secure:
            raise ValueError("SameSite=None requiere cookies Secure.")
        if self.environment == "production" and not self.cookie_secure:
            raise ValueError("Producción requiere cookies Secure.")
        return self


def get_settings() -> Settings:
    load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False)
    database_url = os.getenv("DATABASE_URL", "").strip()
    origins = os.getenv("CORS_ORIGINS")
    values = {"database_url": SecretStr(database_url) if database_url else None}
    values.update(
        environment=os.getenv("ENVIRONMENT", "development"),
        cookie_secure=os.getenv("COOKIE_SECURE", "false"),
        cookie_samesite=os.getenv("COOKIE_SAMESITE", "lax"),
        session_ttl_seconds=os.getenv("SESSION_TTL_SECONDS", "28800"),
        csrf_trusted_origins=[o.strip() for o in os.getenv("CSRF_TRUSTED_ORIGINS", "").split(",") if o.strip()],
    )
    if origins is not None:
        values["cors_origins"] = [origin.strip() for origin in origins.split(",") if origin.strip()]
    return Settings(**values)
