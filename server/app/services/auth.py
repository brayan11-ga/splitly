"""Sesiones opacas: tokens aleatorios en cookie, únicamente hashes en PostgreSQL."""

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

from pwdlib import PasswordHash
from sqlalchemy.exc import IntegrityError
from sqlmodel import Session

from app.config import Settings
from app.db.auth_repository import find_session, find_user_by_email
from app.models import AuthSession, User
from app.services.errors import ConflictError

password_hash = PasswordHash.recommended()
# Coste Argon2 también para correos inexistentes, sin respuesta diferenciada.
dummy_hash = password_hash.hash(secrets.token_urlsafe(32))


class AuthenticationError(Exception):
    pass


def digest_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


def csrf_token(token: str) -> str:
    return hmac.new(token.encode(), b"splitly-csrf-v1", hashlib.sha256).hexdigest()


def resolve_session(session: Session, token: str | None) -> tuple[AuthSession, User]:
    record = find_session(session, digest_token(token)) if token and len(token) <= 128 else None
    if record is None or record.expires_at <= datetime.now(timezone.utc):
        raise AuthenticationError("Sesión no válida o expirada.")
    user = session.get(User, record.user_id)
    if user is None:
        raise AuthenticationError("Sesión no válida o expirada.")
    return record, user


def new_session(session: Session, user: User, settings: Settings, previous_token: str | None) -> str:
    if previous_token and len(previous_token) <= 128:
        previous = find_session(session, digest_token(previous_token))
        if previous is not None:
            session.delete(previous)
    token = secrets.token_urlsafe(32)
    session.add(AuthSession(
        token_hash=digest_token(token), user_id=user.id,
        expires_at=datetime.now(timezone.utc) + timedelta(seconds=settings.session_ttl_seconds),
    ))
    return token


def register(session: Session, full_name: str, email: str, password: str,
             settings: Settings, previous_token: str | None) -> tuple[User, str]:
    if find_user_by_email(session, email) is not None:
        raise ConflictError("No se pudo registrar este correo. Prueba iniciar sesión.")
    user = User(full_name=full_name, email=email, hashed_password=password_hash.hash(password))
    session.add(user)
    try:
        session.flush()  # La restricción UNIQUE resuelve también registros concurrentes.
        token = new_session(session, user, settings, previous_token)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise ConflictError("No se pudo registrar este correo. Prueba iniciar sesión.") from None
    session.refresh(user)
    return user, token


def login(session: Session, email: str, password: str, settings: Settings,
          previous_token: str | None) -> tuple[User, str]:
    user = find_user_by_email(session, email)
    valid = password_hash.verify(password, user.hashed_password if user else dummy_hash)
    if user is None or not valid:
        raise AuthenticationError("Correo o contraseña incorrectos.")
    token = new_session(session, user, settings, previous_token)
    session.commit()
    return user, token


def logout(session: Session, record: AuthSession) -> None:
    session.delete(record)
    session.commit()
