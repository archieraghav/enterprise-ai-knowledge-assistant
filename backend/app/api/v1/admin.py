import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import require_role
from app.db.session import get_db
from app.models.user import User
from app.schemas.admin import (
    AdminUserListResponse,
    AdminUserResponse,
    OrganizationMetricsResponse,
    UpdateUserRoleRequest,
)
from app.services.admin_service import get_organization_metrics, list_organization_users, update_user_role

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/users", response_model=AdminUserListResponse)
async def get_organization_users(
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
) -> AdminUserListResponse:
    users, total = await list_organization_users(db, current_user.organization_id)
    return AdminUserListResponse(
        items=[AdminUserResponse.model_validate(u) for u in users],
        total=total,
    )


@router.patch("/users/{user_id}/role", response_model=AdminUserResponse)
async def patch_user_role(
    user_id: uuid.UUID,
    payload: UpdateUserRoleRequest,
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
) -> AdminUserResponse:
    updated_user = await update_user_role(db, current_user.organization_id, user_id, payload.role)
    return AdminUserResponse.model_validate(updated_user)


@router.get("/metrics", response_model=OrganizationMetricsResponse)
async def get_metrics(
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
) -> OrganizationMetricsResponse:
    metrics = await get_organization_metrics(db, current_user.organization_id)
    return OrganizationMetricsResponse(**metrics)