from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ValidationException
from app.models.user import User
from app.schemas.user import DeactivateAccountRequest, UserProfileUpdateRequest


async def update_profile(db: AsyncSession, user: User, payload: UserProfileUpdateRequest) -> User:
    """Apply partial updates to a user's profile fields."""
    if payload.full_name is not None:
        user.full_name = payload.full_name

    await db.commit()
    await db.refresh(user)
    return user


async def deactivate_account(db: AsyncSession, user: User, payload: DeactivateAccountRequest) -> User:
    """Deactivate a user's own account after explicit confirmation."""
    if not payload.confirm:
        raise ValidationException("Deactivation must be explicitly confirmed")

    user.is_active = False
    await db.commit()
    await db.refresh(user)
    return user