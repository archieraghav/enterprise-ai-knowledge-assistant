import uuid
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.conversation import ConversationMessage, Conversation
from app.models.feedback import Feedback


async def get_daily_query_counts(db: AsyncSession, organization_id: uuid.UUID, days: int = 7) -> list[dict]:
    """Return the number of user questions asked per day, for the last N days."""
    since = datetime.now(timezone.utc) - timedelta(days=days)

    result = await db.execute(
        select(
            func.date(ConversationMessage.created_at).label("day"),
            func.count().label("count"),
        )
        .join(Conversation, Conversation.id == ConversationMessage.conversation_id)
        .where(
            Conversation.organization_id == organization_id,
            ConversationMessage.role == "user",
            ConversationMessage.created_at >= since,
        )
        .group_by(func.date(ConversationMessage.created_at))
        .order_by(func.date(ConversationMessage.created_at))
    )

    return [{"day": row.day, "count": row.count} for row in result.all()]


async def get_total_query_count(db: AsyncSession, organization_id: uuid.UUID) -> int:
    """Return the all-time total number of user questions asked."""
    result = await db.execute(
        select(func.count())
        .select_from(ConversationMessage)
        .join(Conversation, Conversation.id == ConversationMessage.conversation_id)
        .where(
            Conversation.organization_id == organization_id,
            ConversationMessage.role == "user",
        )
    )
    return result.scalar_one()


async def get_feedback_summary(db: AsyncSession, organization_id: uuid.UUID) -> dict:
    """Summarize feedback counts and positive rate for an organization."""
    total_result = await db.execute(
        select(func.count()).select_from(Feedback).where(Feedback.organization_id == organization_id)
    )
    total = total_result.scalar_one()

    positive_result = await db.execute(
        select(func.count())
        .select_from(Feedback)
        .where(Feedback.organization_id == organization_id, Feedback.is_positive.is_(True))
    )
    positive = positive_result.scalar_one()

    negative = total - positive
    positive_rate = round(positive / total, 4) if total > 0 else 0.0

    return {
        "total_feedback": total,
        "positive_count": positive,
        "negative_count": negative,
        "positive_rate": positive_rate,
    }