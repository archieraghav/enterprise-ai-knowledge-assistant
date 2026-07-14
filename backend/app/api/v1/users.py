from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.user import (
    DeactivateAccountRequest,
    UserProfileResponse,
    UserProfileUpdateRequest,
)
from app.services.user_service import deactivate_account, update_profile

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserProfileResponse)
async def get_profile(current_user: User = Depends(get_current_active_user)) -> UserProfileResponse:
    return UserProfileResponse.model_validate(current_user)


@router.patch("/me", response_model=UserProfileResponse)
async def patch_profile(
    payload: UserProfileUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> UserProfileResponse:
    updated_user = await update_profile(db, current_user, payload)
    return UserProfileResponse.model_validate(updated_user)


@router.post("/me/deactivate", response_model=UserProfileResponse)
async def deactivate_my_account(
    payload: DeactivateAccountRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> UserProfileResponse:
    deactivated_user = await deactivate_account(db, current_user, payload)
    return UserProfileResponse.model_validate(deactivated_user)