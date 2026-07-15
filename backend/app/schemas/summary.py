import uuid

from pydantic import BaseModel, Field


class SummarizeRequest(BaseModel):
    document_ids: list[uuid.UUID] = Field(min_length=1, max_length=10)


class SummarizeResponse(BaseModel):
    summary: str
    document_titles: list[str]