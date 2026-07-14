from fastapi import FastAPI

from app.core.config import settings

app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
)


@app.get("/health", tags=["system"])
async def health_check() -> dict[str, str]:
    """Basic liveness probe used by orchestration and monitoring tools."""
    return {"status": "ok", "environment": settings.environment}