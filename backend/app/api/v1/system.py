from fastapi import APIRouter, Depends

from app.core.config import settings
from app.core.rbac import require_role
from app.models.user import User

router = APIRouter(tags=["system"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Basic liveness probe used by orchestration and monitoring tools."""
    return {"status": "ok", "environment": settings.environment}


@router.get("/admin-only")
async def admin_only_route(current_user: User = Depends(require_role("admin"))) -> dict[str, str]:
    """Temporary test route to verify RBAC — removed once real admin endpoints exist (Day 47)."""
    return {"message": f"Welcome, {current_user.full_name}. You have admin access."}