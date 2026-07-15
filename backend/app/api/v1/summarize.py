from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.llm import get_llm
from app.ai.prompts.summary_prompt import SUMMARY_SYSTEM_PROMPT, build_summary_prompt
from app.api.dependencies import get_current_active_user
from app.core.exceptions import ValidationException
from app.db.session import get_db
from app.models.user import User
from app.schemas.summary import SummarizeRequest, SummarizeResponse
from app.services.document_service import get_document

router = APIRouter(prefix="/summarize", tags=["ai-features"])


@router.post("", response_model=SummarizeResponse)
async def summarize_documents(
    payload: SummarizeRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> SummarizeResponse:
    titles = []
    texts = []

    for document_id in payload.document_ids:
        document = await get_document(db, current_user.organization_id, document_id)
        if not document.extracted_text:
            raise ValidationException(f"Document '{document.title}' has no extracted text to summarize")
        titles.append(document.title)
        texts.append(document.extracted_text)

    prompt = build_summary_prompt(titles, texts)
    llm = get_llm()
    summary = await llm.generate(prompt, system_prompt=SUMMARY_SYSTEM_PROMPT)

    return SummarizeResponse(summary=summary, document_titles=titles)