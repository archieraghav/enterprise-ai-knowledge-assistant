from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.rbac import require_role
from app.db.session import get_db
from app.models.user import User
from app.schemas.analytics import AnalyticsResponse, DailyQueryCount, FeedbackSummary
from app.services.analytics_service import (
    get_daily_query_counts,
    get_feedback_summary,
    get_total_query_count,
)

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("", response_model=AnalyticsResponse)
async def get_analytics(
    current_user: User = Depends(require_role("admin")),
    db: AsyncSession = Depends(get_db),
) -> AnalyticsResponse:
    daily_counts = await get_daily_query_counts(db, current_user.organization_id, days=7)
    total_queries = await get_total_query_count(db, current_user.organization_id)
    feedback_summary = await get_feedback_summary(db, current_user.organization_id)

    return AnalyticsResponse(
        queries_last_7_days=[DailyQueryCount(**row) for row in daily_counts],
        total_queries=total_queries,
        feedback_summary=FeedbackSummary(**feedback_summary),
    )