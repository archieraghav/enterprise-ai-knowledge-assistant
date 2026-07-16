from fastapi import APIRouter, Depends, Request

from app.ai.graphs.rag_graph import get_rag_graph
from app.api.dependencies import get_current_active_user
from app.middleware.rate_limiter import limiter
from app.models.user import User
from app.schemas.qa import AskRequest, AskResponse, CitationResponse

router = APIRouter(prefix="/qa", tags=["question-answering"])


@router.post("/ask", response_model=AskResponse)
@limiter.limit("20/minute")
async def ask_question(
    request: Request,
    payload: AskRequest,
    current_user: User = Depends(get_current_active_user),
) -> AskResponse:
    graph = get_rag_graph()

    result = await graph.ainvoke(
        {
            "organization_id": current_user.organization_id,
            "question": payload.question,
        }
    )

    return AskResponse(
        answer=result["answer"],
        citations=[
            CitationResponse(
                document_id=c.document_id,
                document_title=c.document_title,
                excerpt=c.excerpt,
            )
            for c in result["citations"]
        ],
    )