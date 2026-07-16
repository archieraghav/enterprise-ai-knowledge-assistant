import uuid
from datetime import date

from pydantic import BaseModel


class DailyQueryCount(BaseModel):
    day: date
    count: int


class TopDocument(BaseModel):
    document_id: uuid.UUID
    document_title: str
    conversation_mentions: int


class FeedbackSummary(BaseModel):
    total_feedback: int
    positive_count: int
    negative_count: int
    positive_rate: float


class AnalyticsResponse(BaseModel):
    queries_last_7_days: list[DailyQueryCount]
    total_queries: int
    feedback_summary: FeedbackSummary