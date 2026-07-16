from fastapi import APIRouter
from sqlalchemy import text

from app.ai.vectorstore.chroma_client import get_chroma_client
from app.core.config import settings
from app.core.logging import get_logger
from app.db.session import AsyncSessionLocal

router = APIRouter(tags=["system"])
logger = get_logger(__name__)


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Basic liveness probe — confirms the app process itself is running."""
    return {"status": "ok", "environment": settings.environment}


@router.get("/ready")
async def readiness_check() -> dict[str, str]:
    """Readiness probe — confirms the app's actual dependencies (DB, vector store) are reachable.

    Returns 'degraded' rather than raising an error if a dependency is down,
    since a partial outage (e.g. ChromaDB down but Postgres fine) shouldn't
    necessarily take the whole app out of a load balancer's rotation —
    that's a deployment-specific decision left to the orchestrator.
    """
    checks = {"database": "unknown", "vector_store": "unknown"}

    try:
        async with AsyncSessionLocal() as db:
            await db.execute(text("SELECT 1"))
        checks["database"] = "ok"
    except Exception:
        logger.exception("Readiness check: database unreachable")
        checks["database"] = "unreachable"

    try:
        client = get_chroma_client()
        client.heartbeat()
        checks["vector_store"] = "ok"
    except Exception:
        logger.exception("Readiness check: vector store unreachable")
        checks["vector_store"] = "unreachable"

    overall_status = "ok" if all(v == "ok" for v in checks.values()) else "degraded"

    return {"status": overall_status, **checks}