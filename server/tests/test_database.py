from io import StringIO
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pytest
from alembic import command
from alembic.config import Config
from sqlalchemy import create_mock_engine
from sqlmodel import SQLModel

from app.config import Settings
from app.db.check import main
from app.db.session import get_database_url, get_session
from app.models import Group, Member


def test_postgresql_url_validation():
    assert get_database_url("postgresql://user:placeholder@localhost/splitly_dev").drivername == "postgresql+psycopg"
    for value in ["sqlite://", "not-a-url", "postgresql://localhost:invalid/db"]:
        with pytest.raises(RuntimeError):
            get_database_url(value)


def test_session_lifecycle():
    request = SimpleNamespace(app=SimpleNamespace(state=SimpleNamespace(
        settings=Settings(database_url="postgresql://localhost/splitly_dev")
    )))
    with patch("app.db.session.get_engine"), patch("app.db.session.Session") as session:
        dependency = get_session(request)
        assert next(dependency) is session.return_value.__enter__.return_value
        dependency.close()
        session.return_value.__exit__.assert_called_once()


def test_connection_check_refuses_remote_and_hides_secret(capsys):
    with patch("app.db.check.get_settings", return_value=Settings(
        database_url="postgresql://user:private-password@example.org/splitly_dev"
    )), patch("app.db.check.get_engine") as engine:
        assert main() == 1
        engine.assert_not_called()
    assert "private-password" not in capsys.readouterr().out


def test_connection_check_handles_failure_without_credentials(capsys):
    with patch("app.db.check.get_settings", return_value=Settings(
        database_url="postgresql://user:private-password@localhost/splitly_dev"
    )), patch("app.db.check.get_engine", side_effect=RuntimeError("private-password")):
        assert main() == 1
    assert "private-password" not in capsys.readouterr().out


def test_initial_migration_offline_matches_model_ddl():
    output = StringIO()
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"), output_buffer=output)
    with patch("app.config.get_settings", return_value=Settings(
        database_url="postgresql://user:private-password@localhost/splitly_dev"
    )):
        command.upgrade(config, "head", sql=True)
    sql = output.getvalue()
    statements = []
    engine = create_mock_engine("postgresql+psycopg://", lambda statement, *args, **kwargs:
        statements.append(str(statement.compile(dialect=engine.dialect))))
    SQLModel.metadata.create_all(engine)
    normalize = lambda value: " ".join(value.split()).replace(" ;", ";").rstrip(";")
    normalized_sql = normalize(sql)
    for statement in statements:
        assert normalize(statement) in normalized_sql
    assert "DROP TABLE" not in sql
    assert "private-password" not in sql
    assert set(SQLModel.metadata.tables) == {"groups", "members"}
    assert Group(name="Viaje").created_at.tzinfo is not None
    assert Member.__table__.c.group_id.index
