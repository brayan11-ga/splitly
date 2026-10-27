from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.config import Settings, get_settings
from app.routers.health import router as health_router
from app.routers.groups import router as groups_router
from app.routers.members import router as members_router
from app.routers.expenses import router as expenses_router
from app.services.errors import ConflictError, InputError, NotFoundError
from app.routers.auth import router as auth_router
from app.services.auth import AuthenticationError


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings if settings is not None else get_settings()
    application = FastAPI(title="Splitly API", version="0.1.0")
    application.state.settings = settings
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["Content-Type", "X-CSRF-Token"],
    )
    application.include_router(health_router, prefix="/api")
    application.include_router(groups_router, prefix="/api")
    application.include_router(members_router, prefix="/api")
    application.include_router(expenses_router, prefix="/api")
    application.include_router(auth_router, prefix="/api")

    @application.middleware("http")
    async def private_responses(request, call_next):
        response = await call_next(request)
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store"
            response.headers["X-Content-Type-Options"] = "nosniff"
        return response

    @application.exception_handler(AuthenticationError)
    async def authentication_error(request, exc):
        return JSONResponse(status_code=401, content={"detail": str(exc)})

    @application.exception_handler(RequestValidationError)
    async def validation_error(request, exc):
        # FastAPI incluye input por defecto: nunca reflejar contraseñas recibidas.
        errors = [{k: error[k] for k in ("loc", "msg", "type")} for error in exc.errors()]
        return JSONResponse(status_code=422, content={"detail": errors})

    @application.exception_handler(NotFoundError)
    async def not_found_handler(request, exc):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @application.exception_handler(ConflictError)
    async def conflict_handler(request, exc):
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @application.exception_handler(InputError)
    async def input_error_handler(request, exc):
        return JSONResponse(status_code=422, content={"detail": str(exc)})

    @application.exception_handler(SQLAlchemyError)
    async def database_error_handler(request, exc):
        # Las excepciones del driver pueden incluir SQL y detalles sensibles.
        return JSONResponse(status_code=500, content={"detail": "No se pudo completar la operación de base de datos."})

    return application


app = create_app()
