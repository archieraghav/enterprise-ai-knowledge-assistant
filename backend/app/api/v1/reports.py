from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.llm import get_llm
from app.ai.prompts.report_prompt import REPORT_SYSTEM_PROMPT, build_report_prompt
from app.api.dependencies import get_current_active_user
from app.core.exceptions import ValidationException
from app.db.session import get_db
from app.models.user import User
from app.schemas.report import GenerateReportRequest, GenerateReportResponse
from app.services.document_service import get_document

router = APIRouter(prefix="/reports", tags=["ai-features"])


@router.post("/generate", response_model=GenerateReportResponse)
async def generate_report(
    payload: GenerateReportRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> GenerateReportResponse:
    titles = []
    texts = []

    for document_id in payload.document_ids:
        document = await get_document(db, current_user.organization_id, document_id)
        if not document.extracted_text:
            raise ValidationException(f"Document '{document.title}' has no extracted text")
        titles.append(document.title)
        texts.append(document.extracted_text)

    prompt = build_report_prompt(payload.title, titles, texts)
    llm = get_llm()
    content_markdown = await llm.generate(prompt, system_prompt=REPORT_SYSTEM_PROMPT)

    return GenerateReportResponse(
        title=payload.title,
        content_markdown=content_markdown,
        source_documents=titles,
    )


@router.post("/generate/export", response_class=PlainTextResponse)
async def generate_report_export(
    payload: GenerateReportRequest,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> str:
    """Same as /generate, but returns raw markdown text for direct file download."""
    result = await generate_report(payload, current_user, db)
    return result.content_markdown