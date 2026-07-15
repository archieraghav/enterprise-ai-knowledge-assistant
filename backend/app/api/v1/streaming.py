import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from app.ai.citation_formatter import format_citations
from app.ai.llm import get_llm
from app.ai.prompts.qa_prompt import SYSTEM_PROMPT, build_qa_prompt
from app.ai.retriever import retrieve_relevant_chunks
from app.api.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.qa import AskRequest

router = APIRouter(prefix="/qa", tags=["question-answering"])


@router.post("/ask/stream")
async def ask_question_streaming(
    payload: AskRequest,
    current_user: User = Depends(get_current_active_user),
) -> StreamingResponse:
    """Stream an answer token-by-token, sending citations as a final event."""

    async def event_generator():
        chunks = retrieve_relevant_chunks(
            organization_id=current_user.organization_id,
            query=payload.question,
            top_k=5,
        )

        if not chunks:
            message = "I couldn't find any relevant information in the uploaded documents to answer this question."
            yield f"data: {json.dumps({'type': 'token', 'content': message})}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'citations': []})}\n\n"
            return

        prompt = build_qa_prompt(payload.question, chunks)
        llm = get_llm()

        async for token in llm.generate_stream(prompt, system_prompt=SYSTEM_PROMPT):
            yield f"data: {json.dumps({'type': 'token', 'content': token})}\n\n"

        citations = format_citations(chunks)
        citations_data = [
            {"document_id": c.document_id, "document_title": c.document_title, "excerpt": c.excerpt}
            for c in citations
        ]
        yield f"data: {json.dumps({'type': 'done', 'citations': citations_data})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")