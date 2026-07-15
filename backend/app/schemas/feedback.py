import uuid
from datetime import datetime

from pydantic import BaseModel, Field


class SubmitFeedbackRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    answer: str = Field(min_length=1)
    is_positive: bool
    comment: str | None = Field(default=None, max_length=1000)


class FeedbackResponse(BaseModel):
    id: uuid.UUID
    is_positive: bool
    created_at: datetime

    model_config = {"from_attributes": True}