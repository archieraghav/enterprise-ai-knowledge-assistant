import uuid

from pydantic import BaseModel, Field


class GenerateReportRequest(BaseModel):
    title: str = Field(min_length=1, max_length=255)
    document_ids: list[uuid.UUID] = Field(min_length=1, max_length=10)


class GenerateReportResponse(BaseModel):
    title: str
    content_markdown: str
    source_documents: list[str]