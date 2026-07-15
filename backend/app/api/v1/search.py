from fastapi import APIRouter, Depends

from app.ai.retriever import retrieve_relevant_chunks
from app.ai.vectorstore.metadata_filters import MetadataFilter
from app.api.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.search import SearchRequest, SearchResponse, SearchResultItem

router = APIRouter(prefix="/search", tags=["ai-features"])


@router.post("", response_model=SearchResponse)
async def search_knowledge_base(
    payload: SearchRequest,
    current_user: User = Depends(get_current_active_user),
) -> SearchResponse:
    metadata_filter = MetadataFilter(file_types=payload.file_types or [])

    chunks = retrieve_relevant_chunks(
        organization_id=current_user.organization_id,
        query=payload.query,
        top_k=payload.top_k,
        metadata_filter=metadata_filter,
    )

    results = [
        SearchResultItem(
            document_id=chunk.document_id,
            document_title=chunk.document_title,
            content=chunk.content,
            # Convert L2 distance to a friendlier 0-1 relevance score
            # (lower distance = higher relevance).
            relevance_score=round(1 / (1 + chunk.distance), 4),
        )
        for chunk in chunks
    ]

    return SearchResponse(query=payload.query, results=results)