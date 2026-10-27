from fastapi import APIRouter, Depends, Request, Response

from app.routers.auth_dependencies import CurrentUser, require_auth_origin
from app.routers.dependencies import SessionDep
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, UserRead
from app.services import auth

router = APIRouter(prefix="/auth", tags=["auth"])


def authenticated_response(request: Request, response: Response, user, token: str) -> AuthResponse:
    settings = request.app.state.settings
    response.set_cookie(
        settings.cookie_name, token, httponly=True, secure=settings.cookie_secure,
        samesite=settings.cookie_samesite, max_age=settings.session_ttl_seconds, path="/",
    )
    return AuthResponse(user=UserRead.model_validate(user), csrf_token=auth.csrf_token(token))


@router.post("/register", status_code=201, response_model=AuthResponse, dependencies=[Depends(require_auth_origin)])
def register(payload: RegisterRequest, request: Request, response: Response, session: SessionDep):
    settings = request.app.state.settings
    user, token = auth.register(session, payload.full_name, str(payload.email), payload.password,
                                settings, request.cookies.get(settings.cookie_name))
    return authenticated_response(request, response, user, token)


@router.post("/login", response_model=AuthResponse, dependencies=[Depends(require_auth_origin)])
def login(payload: LoginRequest, request: Request, response: Response, session: SessionDep):
    settings = request.app.state.settings
    user, token = auth.login(session, str(payload.email), payload.password,
                             settings, request.cookies.get(settings.cookie_name))
    return authenticated_response(request, response, user, token)


@router.get("/me", response_model=AuthResponse)
def me(request: Request, user: CurrentUser):
    token = request.cookies[request.app.state.settings.cookie_name]
    return AuthResponse(user=UserRead.model_validate(user), csrf_token=auth.csrf_token(token))


@router.post("/logout", status_code=204)
def logout(request: Request, user: CurrentUser, session: SessionDep):
    auth.logout(session, request.state.auth_session)
    settings = request.app.state.settings
    response = Response(status_code=204)
    response.delete_cookie(settings.cookie_name, path="/", secure=settings.cookie_secure,
                           httponly=True, samesite=settings.cookie_samesite)
    return response
