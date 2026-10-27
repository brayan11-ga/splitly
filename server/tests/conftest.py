"""Integración PostgreSQL en una base temporal; nunca escribe en splitly_dev."""

import os
from contextlib import contextmanager
from pathlib import Path
from unittest.mock import patch
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlmodel import Session

from app.config import Settings, get_settings
from app.db.session import get_database_url, get_session
from app.main import create_app


@contextmanager
def temporary_postgres():
    settings = get_settings()  # Carga server/.env sin imprimir su contenido.
    source = os.getenv("TEST_DATABASE_URL") or (
        settings.database_url.get_secret_value() if settings.database_url else None
    )
    if not source:
        pytest.fail("Configura una conexión PostgreSQL local para crear la base temporal de pruebas.", pytrace=False)
    try:
        url = get_database_url(source)
    except RuntimeError:
        pytest.fail("La configuración PostgreSQL de pruebas no es válida.", pytrace=False)
    if url.host not in {"localhost", "127.0.0.1", "::1"}:
        pytest.fail("Las pruebas solo permiten PostgreSQL local; se rechazó el host remoto.", pytrace=False)

    database_name = f"splitly_test_{uuid4().hex}"
    assert database_name.startswith("splitly_test_") and len(database_name) == 45
    admin = create_engine(
        url.set(database="postgres"), isolation_level="AUTOCOMMIT",
        connect_args={"connect_timeout": 5}, hide_parameters=True,
    )
    engine = None
    created = False
    try:
        try:
            with admin.connect() as connection:
                connection.exec_driver_sql(f'CREATE DATABASE "{database_name}"')
            created = True
            test_url = url.set(database=database_name)
            engine = create_engine(test_url, connect_args={"connect_timeout": 5}, hide_parameters=True)
            config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
            with patch("app.config.get_settings", return_value=Settings(
                database_url=test_url.render_as_string(hide_password=False)
            )):
                command.upgrade(config, "0001_groups_members")
                # Datos previos: verificar la actualización sin usar splitly_dev.
                legacy_group = uuid4()
                with engine.begin() as connection:
                    connection.execute(text("INSERT INTO groups (id, name) VALUES (:id, 'pre-auth legacy')"), {"id": legacy_group})
                    connection.execute(text("INSERT INTO members (id, group_id, name) VALUES (:id, :group_id, 'legacy member')"),
                                       {"id": uuid4(), "group_id": legacy_group})
                command.upgrade(config, "head")
                command.check(config)
        except Exception:
            pytest.fail(
                "No se pudo preparar PostgreSQL de pruebas. Comprueba conexión local y permiso CREATEDB; no se modificó splitly_dev.",
                pytrace=False,
            )
        yield engine
    finally:
        if engine is not None:
            engine.dispose()
        if created:
            # Solo se elimina la base aleatoria creada por ESTA ejecución.
            assert database_name.startswith("splitly_test_") and len(database_name) == 45
            try:
                with admin.connect() as connection:
                    connection.exec_driver_sql(f'DROP DATABASE "{database_name}"')
            except Exception:
                pytest.fail(f"No se pudo retirar la base temporal {database_name}; revisar manualmente.", pytrace=False)
        admin.dispose()


@pytest.fixture(scope="session")
def postgres_engine():
    with temporary_postgres() as engine:
        yield engine


@pytest.fixture
def db_connection(postgres_engine):
    with postgres_engine.connect() as connection:
        transaction = connection.begin()
        try:
            yield connection
        finally:
            transaction.rollback()


@pytest.fixture
def raw_client(db_connection):
    def override_session():
        with Session(bind=db_connection, join_transaction_mode="create_savepoint") as session:
            yield session

    application = create_app(Settings())
    application.dependency_overrides[get_session] = override_session
    with TestClient(application, headers={"Origin": "http://localhost:5173", "X-CSRF-Token": "bootstrap"}) as client:
        yield client


@pytest.fixture
def api_client(raw_client):
    response = raw_client.post("/api/auth/register", json={
        "full_name": "Persona de prueba", "email": f"{uuid4().hex}@example.com",
        "password": "Una frase de prueba segura 123",
    })
    assert response.status_code == 201
    raw_client.headers["X-CSRF-Token"] = response.json()["csrf_token"]
    return raw_client
