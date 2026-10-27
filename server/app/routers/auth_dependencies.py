import secrets
from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request

from app.models import User
from app.routers.dependencies import SessionDep
from app.services import auth


def require_origin(request: Request) -> None:
    if request.headers.get("origin") not in request.app.state.settings.trusted_origins:
        raise HTTPException(status_code=403, detail="Origen no autorizado.")


def require_auth_origin(request: Request, x_csrf_token: Annotated[str | None, Header()] = None) -> None:
    require_origin(request)
    # Cabecera no simple: exige preflight en navegadores, incluso antes del login.
    if not x_csrf_token:
        raise HTTPException(status_code=403, detail="Falta protección CSRF.")


def get_current_user(request: Request, session: SessionDep,
                     x_csrf_token: Annotated[str | None, Header()] = None) -> User:
    settings = request.app.state.settings
    token = request.cookies.get(settings.cookie_name)
    record, user = auth.resolve_session(session, token)
    if request.method not in {"GET", "HEAD", "OPTIONS"}:
        require_origin(request)
        if not secrets.compare_digest((x_csrf_token or "").encode(), auth.csrf_token(token).encode()):
            raise HTTPException(status_code=403, detail="Token CSRF no válido.")
    request.state.auth_session = record
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]
