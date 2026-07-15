import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundException, ValidationException
from app.core.rbac import ROLE_HIERARCHY
from app.models.conversation import Conversation
from app.models.document import Document
from app.models.user import User


async def list_organization_users(db: AsyncSession, organization_id: uuid.UUID) -> tuple[list[User], int]:
    """Return all users belonging to an organization."""
    result = await db.execute(select(User).where(User.organization_id == organization_id))
    users = list(result.scalars().all())
    return users, len(users)


async def update_user_role(
    db: AsyncSession, organization_id: uuid.UUID, target_user_id: uuid.UUID, new_role: str
) -> User:
    """Update a user's role, scoped to the admin's own organization."""
    if new_role not in ROLE_HIERARCHY:
        raise ValidationException(f"Invalid role. Must be one of: {', '.join(ROLE_HIERARCHY)}")

    result = await db.execute(
        select(User).where(User.id == target_user_id, User.organization_id == organization_id)
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise NotFoundException("User not found in your organization")

    user.role = new_role
    await db.commit()
    await db.refresh(user)
    return user


async def get_organization_metrics(db: AsyncSession, organization_id: uuid.UUID) -> dict:
    """Compute basic usage metrics for an organization's admin dashboard."""
    total_users = (
        await db.execute(select(func.count()).select_from(User).where(User.organization_id == organization_id))
    ).scalar_one()

    active_users = (
        await db.execute(
            select(func.count())
            .select_from(User)
            .where(User.organization_id == organization_id, User.is_active.is_(True))
        )
    ).scalar_one()

    total_documents = (
        await db.execute(
            select(func.count())
            .select_from(Document)
            .where(Document.organization_id == organization_id, Document.is_deleted.is_(False))
        )
    ).scalar_one()

    indexed_documents = (
        await db.execute(
            select(func.count())
            .select_from(Document)
            .where(
                Document.organization_id == organization_id,
                Document.is_deleted.is_(False),
                Document.status == "indexed",
            )
        )
    ).scalar_one()

    failed_documents = (
        await db.execute(
            select(func.count())
            .select_from(Document)
            .where(
                Document.organization_id == organization_id,
                Document.is_deleted.is_(False),
                Document.status == "failed",
            )
        )
    ).scalar_one()

    total_conversations = (
        await db.execute(
            select(func.count()).select_from(Conversation).where(Conversation.organization_id == organization_id)
        )
    ).scalar_one()

    return {
        "total_users": total_users,
        "active_users": active_users,
        "total_documents": total_documents,
        "indexed_documents": indexed_documents,
        "failed_documents": failed_documents,
        "total_conversations": total_conversations,
    }