import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.feedback import Feedback
from app.schemas.feedback import SubmitFeedbackRequest


async def submit_feedback(
    db: AsyncSession,
    organization_id: uuid.UUID,
    user_id: uuid.UUID,
    payload: SubmitFeedbackRequest,
) -> Feedback:
    """Record a user's feedback on an AI-generated answer."""
    feedback = Feedback(
        organization_id=organization_id,
        user_id=user_id,
        question=payload.question,
        answer=payload.answer,
        is_positive=payload.is_positive,
        comment=payload.comment,
    )
    db.add(feedback)
    await db.commit()
    await db.refresh(feedback)
    return feedback