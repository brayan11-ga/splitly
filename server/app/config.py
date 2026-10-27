"""Configuración del servidor; nunca se comparte con Vite."""

import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field, SecretStr


class Settings(BaseModel):
    database_url: SecretStr | None = None
    cors_origins: list[str] = Field(
        default_factory=lambda: ["http://localhost:5173", "http://127.0.0.1:5173"]
    )


def get_settings() -> Settings:
    load_dotenv(Path(__file__).resolve().parents[1] / ".env", override=False)
    database_url = os.getenv("DATABASE_URL", "").strip()
    origins = os.getenv("CORS_ORIGINS")
    values = {"database_url": SecretStr(database_url) if database_url else None}
    if origins is not None:
        values["cors_origins"] = [origin.strip() for origin in origins.split(",") if origin.strip()]
    return Settings(**values)
