from collections.abc import Iterator
from functools import lru_cache

from fastapi import Request
from sqlalchemy.engine import Engine, URL, make_url
from sqlalchemy.exc import ArgumentError
from sqlmodel import Session, create_engine

from app.config import Settings


def get_database_url(database_url: str) -> URL:
    try:
        url = make_url(database_url)
    except (ArgumentError, ValueError):
        raise RuntimeError("DATABASE_URL debe ser una URL PostgreSQL válida.") from None
    if url.drivername not in {"postgresql", "postgresql+psycopg"}:
        raise RuntimeError("DATABASE_URL debe utilizar PostgreSQL con psycopg.")
    return url.set(drivername="postgresql+psycopg")


@lru_cache(maxsize=1)
def get_engine(database_url: str) -> Engine:
    return create_engine(
        get_database_url(database_url), pool_pre_ping=True,
        connect_args={"connect_timeout": 5}, hide_parameters=True,
    )


def get_session(request: Request) -> Iterator[Session]:
    settings: Settings = request.app.state.settings
    if settings.database_url is None:
        raise RuntimeError("Configura DATABASE_URL en server/.env antes de usar PostgreSQL.")
    engine = get_engine(settings.database_url.get_secret_value())
    with Session(engine) as session:
        yield session
