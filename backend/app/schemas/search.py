from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=500)
    top_k: int = Field(default=10, ge=1, le=50)
    file_types: list[str] | None = None


class SearchResultItem(BaseModel):
    document_id: str
    document_title: str
    content: str
    relevance_score: float


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResultItem]