from fastapi import APIRouter

from app.schemas.health import HealthResponse

router = APIRouter(tags=["health"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Comprueba que la API responde, sin comprobar PostgreSQL."""
    return HealthResponse(status="ok")
