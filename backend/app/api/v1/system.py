from fastapi import APIRouter

from app.core.config import settings

router = APIRouter(tags=["system"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Basic liveness probe used by orchestration and monitoring tools."""
    return {"status": "ok", "environment": settings.environment}