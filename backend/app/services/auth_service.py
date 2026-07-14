import re
import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import UnauthorizedException, ValidationException
from app.core.jwt import create_access_token, create_refresh_token
from app.core.security import hash_password, verify_password
from app.models.organization import Organization
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse


def _slugify(name: str) -> str:
    """Convert an organization name into a URL-safe, unique-ish slug."""
    base = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    suffix = uuid.uuid4().hex[:8]
    return f"{base}-{suffix}"


async def register_user(db: AsyncSession, payload: RegisterRequest) -> User:
    """Create a new organization and its first admin user."""
    existing = await db.execute(select(User).where(User.email == payload.email))
    if existing.scalar_one_or_none() is not None:
        raise ValidationException("An account with this email already exists")

    organization = Organization(
        name=payload.organization_name,
        slug=_slugify(payload.organization_name),
    )
    db.add(organization)
    await db.flush()

    user = User(
        organization_id=organization.id,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        full_name=payload.full_name,
        is_superuser=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, payload: LoginRequest) -> TokenResponse:
    """Verify credentials and issue access + refresh tokens."""
    result = await db.execute(select(User).where(User.email == payload.email))
    user = result.scalar_one_or_none()

    if user is None or not verify_password(payload.password, user.hashed_password):
        raise UnauthorizedException("Invalid email or password")

    if not user.is_active:
        raise UnauthorizedException("Account is deactivated")

    return TokenResponse(
        access_token=create_access_token(str(user.id)),
        refresh_token=create_refresh_token(str(user.id)),
    )