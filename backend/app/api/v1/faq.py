from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.llm import get_llm
from app.ai.prompts.faq_prompt import FAQ_SYSTEM_PROMPT, build_faq_prompt
from app.api.dependencies import get_current_active_user
from app.core.exceptions import ValidationException
from app.db.session import get_db
from app.models.user import User
from app.schemas.faq import GenerateFAQRequest, GenerateFAQResponse
from app.services.document_service import get_document
from app.services.faq_service import parse_faq_response

router = APIRouter(prefix="/faq", tags=["ai-features"])


@router.post("/generate", response_model=GenerateFAQResponse)
async def generate_faq(
    payload: GenerateFAQRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> GenerateFAQResponse:
    document = await get_document(db, current_user.organization_id, payload.document_id)
    if not document.extracted_text:
        raise ValidationException(f"Document '{document.title}' has no extracted text")

    prompt = build_faq_prompt(document.title, document.extracted_text)
    llm = get_llm()
    raw_response = await llm.generate(prompt, system_prompt=FAQ_SYSTEM_PROMPT)

    faqs = parse_faq_response(raw_response)

    return GenerateFAQResponse(document_title=document.title, faqs=faqs)