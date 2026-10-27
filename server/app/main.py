from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.exc import SQLAlchemyError

from app.config import Settings, get_settings
from app.routers.health import router as health_router
from app.routers.groups import router as groups_router
from app.routers.members import router as members_router
from app.services.errors import ConflictError, NotFoundError


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings if settings is not None else get_settings()
    application = FastAPI(title="Splitly API", version="0.1.0")
    application.state.settings = settings
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=False,
        allow_methods=["GET", "POST", "PATCH", "DELETE"],
        allow_headers=["Content-Type"],
    )
    application.include_router(health_router, prefix="/api")
    application.include_router(groups_router, prefix="/api")
    application.include_router(members_router, prefix="/api")

    @application.exception_handler(NotFoundError)
    async def not_found_handler(request, exc):
        return JSONResponse(status_code=404, content={"detail": str(exc)})

    @application.exception_handler(ConflictError)
    async def conflict_handler(request, exc):
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @application.exception_handler(SQLAlchemyError)
    async def database_error_handler(request, exc):
        # Las excepciones del driver pueden incluir SQL y detalles sensibles.
        return JSONResponse(status_code=500, content={"detail": "No se pudo completar la operación de base de datos."})

    return application


app = create_app()
