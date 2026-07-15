from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)


class CitationResponse(BaseModel):
    document_id: str
    document_title: str
    excerpt: str


class AskResponse(BaseModel):
    answer: str
    citations: list[CitationResponse]