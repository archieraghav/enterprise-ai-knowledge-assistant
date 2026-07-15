from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.feedback import FeedbackResponse, SubmitFeedbackRequest
from app.services.feedback_service import submit_feedback

router = APIRouter(prefix="/feedback", tags=["feedback"])


@router.post("", response_model=FeedbackResponse, status_code=status.HTTP_201_CREATED)
async def create_feedback(
    payload: SubmitFeedbackRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> FeedbackResponse:
    feedback = await submit_feedback(db, current_user.organization_id, current_user.id, payload)
    return FeedbackResponse.model_validate(feedback)