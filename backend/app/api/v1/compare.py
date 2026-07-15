from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.llm import get_llm
from app.ai.prompts.compare_prompt import COMPARE_SYSTEM_PROMPT, build_compare_prompt
from app.api.dependencies import get_current_active_user
from app.core.exceptions import ValidationException
from app.db.session import get_db
from app.models.user import User
from app.schemas.compare import CompareRequest, CompareResponse
from app.services.document_service import get_document

router = APIRouter(prefix="/compare", tags=["ai-features"])


@router.post("", response_model=CompareResponse)
async def compare_documents(
    payload: CompareRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> CompareResponse:
    document_a = await get_document(db, current_user.organization_id, payload.document_id_a)
    document_b = await get_document(db, current_user.organization_id, payload.document_id_b)

    if not document_a.extracted_text or not document_b.extracted_text:
        raise ValidationException("Both documents must have extracted text to compare")

    prompt = build_compare_prompt(
        document_a.title, document_a.extracted_text,
        document_b.title, document_b.extracted_text,
    )
    llm = get_llm()
    comparison = await llm.generate(prompt, system_prompt=COMPARE_SYSTEM_PROMPT)

    return CompareResponse(
        comparison=comparison,
        document_title_a=document_a.title,
        document_title_b=document_b.title,
    )