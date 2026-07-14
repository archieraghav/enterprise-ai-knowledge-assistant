from fastapi import APIRouter, Depends

from app.api.dependencies import get_current_active_user
from app.core.config import settings
from app.core.rbac import require_role
from app.models.user import User

router = APIRouter(tags=["system"])


@router.get("/health")
async def health_check() -> dict[str, str]:
    """Basic liveness probe used by orchestration and monitoring tools."""
    return {"status": "ok", "environment": settings.environment}


@router.get("/me")
async def read_current_user(current_user: User = Depends(get_current_active_user)) -> dict[str, str]:
    """Return basic info about the currently authenticated, active user."""
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role": current_user.role,
    }


@router.get("/admin-only")
async def admin_only_route(current_user: User = Depends(require_role("admin"))) -> dict[str, str]:
    """Temporary test route to verify RBAC — removed once real admin endpoints exist (Day 47)."""
    return {"message": f"Welcome, {current_user.full_name}. You have admin access."}