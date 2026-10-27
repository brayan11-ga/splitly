from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from pydantic import ValidationError
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session, select

from app.config import Settings
from app.models import AuthSession, Group, Member, User
from app.services.auth import digest_token, password_hash

PASSWORD = "Una contraseña de prueba suficientemente larga 123"


def register(client, email="persona@example.com"):
    return client.post("/api/auth/register", json={
        "full_name": "  Persona de Prueba  ", "email": email, "password": PASSWORD,
    })


def test_register_normalizes_hashes_and_sets_cookie(raw_client, db_connection):
    response = register(raw_client, " PERSONA@EXAMPLE.COM ")
    assert response.status_code == 201
    data = response.json()
    assert data["user"]["email"] == "persona@example.com"
    assert data["user"]["full_name"] == "Persona de Prueba"
    assert "hashed_password" not in response.text and PASSWORD not in response.text
    assert "HttpOnly" in response.headers["set-cookie"]
    assert "SameSite=lax" in response.headers["set-cookie"]
    assert response.headers["cache-control"] == "no-store"
    token = raw_client.cookies.get("splitly_session")
    with Session(db_connection, join_transaction_mode="create_savepoint") as session:
        user = session.exec(select(User).where(User.email == "persona@example.com")).one()
        assert user.hashed_password.startswith("$argon2id$")
        assert password_hash.verify(PASSWORD, user.hashed_password)
        record = session.get(AuthSession, digest_token(token))
        assert record is not None and record.token_hash != token
    assert raw_client.get("/api/auth/me").json() == data


def test_duplicate_and_database_email_constraint(raw_client, db_connection):
    assert register(raw_client).status_code == 201
    assert register(raw_client, "PERSONA@example.com").status_code == 409
    with Session(db_connection, join_transaction_mode="create_savepoint") as session:
        session.add(User(full_name="Otro", email="persona@example.com", hashed_password="not-plaintext"))
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()
        session.add(User(full_name="Otro", email="NOT-NORMALIZED@example.com", hashed_password="not-plaintext"))
        with pytest.raises(IntegrityError):
            session.commit()
        session.rollback()


def test_login_logout_rotation_and_revocation(raw_client):
    assert register(raw_client).status_code == 201
    old_cookie = raw_client.cookies.get("splitly_session")
    response = raw_client.post("/api/auth/login", json={"email": "PERSONA@example.com", "password": PASSWORD})
    assert response.status_code == 200
    assert raw_client.cookies.get("splitly_session") != old_cookie
    new_cookie = raw_client.cookies.get("splitly_session")
    raw_client.cookies.clear()
    raw_client.cookies.set("splitly_session", old_cookie)
    assert raw_client.get("/api/auth/me").status_code == 401
    raw_client.cookies.clear()
    raw_client.cookies.set("splitly_session", new_cookie)
    raw_client.headers["X-CSRF-Token"] = response.json()["csrf_token"]
    assert raw_client.post("/api/auth/logout").status_code == 204
    assert raw_client.get("/api/auth/me").status_code == 401
    raw_client.cookies.set("splitly_session", new_cookie)
    assert raw_client.get("/api/auth/me").status_code == 401


def test_login_errors_are_indistinguishable(raw_client):
    assert register(raw_client).status_code == 201
    wrong_password = raw_client.post("/api/auth/login", json={"email": "persona@example.com", "password": "incorrecta"})
    missing_user = raw_client.post("/api/auth/login", json={"email": "missing@example.com", "password": "incorrecta"})
    assert wrong_password.status_code == missing_user.status_code == 401
    assert wrong_password.json() == missing_user.json()


@pytest.mark.parametrize("payload", [
    {"full_name": "", "email": "valid@example.com", "password": PASSWORD},
    {"full_name": "Ana", "email": "invalid", "password": PASSWORD},
    {"full_name": "Ana", "email": "valid@example.com", "password": "short-secret"},
    {"full_name": "Ana", "email": "valid@example.com", "password": "x" * 129},
    {},
])
def test_invalid_registration_does_not_echo_password(raw_client, payload):
    response = raw_client.post("/api/auth/register", json=payload)
    assert response.status_code == 422
    assert "short-secret" not in response.text and PASSWORD not in response.text
    assert all("input" not in error for error in response.json()["detail"])


def test_unauthenticated_routes(raw_client):
    group = uuid4()
    member = uuid4()
    for method, path in [
        ("get", "/api/auth/me"), ("post", "/api/auth/logout"),
        ("get", "/api/groups"), ("post", "/api/groups"),
        ("get", f"/api/groups/{group}"), ("patch", f"/api/groups/{group}"),
        ("delete", f"/api/groups/{group}"), ("get", f"/api/groups/{group}/members"),
        ("post", f"/api/groups/{group}/members"),
        ("patch", f"/api/groups/{group}/members/{member}"),
        ("delete", f"/api/groups/{group}/members/{member}"),
    ]:
        assert raw_client.request(method, path, json={"name": "Prueba"}).status_code == 401


def test_expired_and_forged_sessions(api_client, db_connection):
    token = api_client.cookies.get("splitly_session")
    with Session(db_connection, join_transaction_mode="create_savepoint") as session:
        record = session.get(AuthSession, digest_token(token))
        record.expires_at = datetime.now(timezone.utc) - timedelta(seconds=1)
        session.add(record)
        session.commit()
    assert api_client.get("/api/auth/me").status_code == 401
    assert api_client.get("/api/groups").status_code == 401
    api_client.cookies.clear()
    api_client.cookies.set("splitly_session", "forged")
    assert api_client.get("/api/auth/me").status_code == 401


def test_csrf_and_origin_protection(api_client):
    for headers in [
        {"X-CSRF-Token": "incorrecto"},
        {"Origin": "https://evil.example"},
        {"Origin": "null"},
    ]:
        assert api_client.post("/api/groups", json={"name": "Blocked"}, headers=headers).status_code == 403
    del api_client.headers["X-CSRF-Token"]
    assert api_client.post("/api/groups", json={"name": "Blocked"}).status_code == 403
    assert api_client.post("/api/auth/login", json={"email": "x@example.com", "password": PASSWORD}).status_code == 403
    api_client.headers["X-CSRF-Token"] = "bootstrap"
    del api_client.headers["Origin"]
    assert register(api_client, "new@example.com").status_code == 403


def test_other_users_cannot_access_groups_or_members(api_client):
    group = api_client.post("/api/groups", json={"name": "Privado"}).json()
    path = f"/api/groups/{group['id']}"
    member = api_client.post(f"{path}/members", json={"name": "Ana"}).json()
    response = register(api_client, "other@example.com")
    assert response.status_code == 201
    api_client.headers["X-CSRF-Token"] = response.json()["csrf_token"]
    assert api_client.get("/api/groups").json() == []
    for method, suffix, payload in [
        ("get", "", None), ("patch", "", {"name": "Ataque"}), ("delete", "", None),
        ("get", "/members", None), ("post", "/members", {"name": "Ataque"}),
        ("patch", f"/members/{member['id']}", {"name": "Ataque"}),
        ("delete", f"/members/{member['id']}", None),
    ]:
        assert api_client.request(method, path + suffix, json=payload).status_code == 404
    assert api_client.post("/api/groups", json={"name": "Ataque", "owner_id": group["id"]}).status_code == 422


def test_migration_preserves_unowned_groups_and_members(api_client, db_connection):
    with Session(db_connection, join_transaction_mode="create_savepoint") as session:
        legacy = session.exec(select(Group).where(Group.name == "pre-auth legacy")).one()
        assert legacy.owner_id is None
        assert session.exec(select(Member).where(Member.group_id == legacy.id)).one().name == "legacy member"
        group_id = legacy.id
    assert api_client.get("/api/groups").json() == []
    assert api_client.get(f"/api/groups/{group_id}").status_code == 404
    assert api_client.delete(f"/api/groups/{group_id}").status_code == 404


def test_production_cookie_configuration_fails_closed():
    for kwargs in [
        {"environment": "production"}, {"cors_origins": ["*"]},
        {"cookie_samesite": "none", "cookie_secure": False},
        {"cors_origins": ["https://example.com/"]},
    ]:
        with pytest.raises(ValidationError):
            Settings(**kwargs)
    settings = Settings(environment="production", cookie_secure=True, cookie_samesite="none",
                        cors_origins=["https://app.example.com"], csrf_trusted_origins=["https://api.example.com"])
    assert settings.cookie_name == "__Host-splitly_session"


def test_production_cookie_has_secure_host_prefix(raw_client):
    raw_client.app.state.settings = Settings(
        environment="production", cookie_secure=True, cookie_samesite="none",
        cors_origins=["https://app.example.com"],
    )
    raw_client.headers["Origin"] = "https://app.example.com"
    response = register(raw_client)
    assert response.status_code == 201
    cookie = response.headers["set-cookie"]
    assert "__Host-splitly_session=" in cookie and "Secure" in cookie and "HttpOnly" in cookie
    assert "SameSite=none" in cookie and "Path=/" in cookie and "Domain=" not in cookie
