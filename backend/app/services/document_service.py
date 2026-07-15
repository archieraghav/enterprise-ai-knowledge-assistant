import uuid

from fastapi import UploadFile
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import NotFoundException, ValidationException
from app.models.document import Document
from app.models.document_version import DocumentVersion
from app.models.user import User
from app.services.storage_service import build_file_key, upload_file
from app.processing.parser_factory import extract_text_from_file

from app.core.logging import get_logger

logger = get_logger(__name__)

ALLOWED_EXTENSIONS = {
    "pdf", "docx", "pptx", "txt", "csv", "xlsx", "xls",
    "png", "jpg", "jpeg", "eml",
}


def _get_extension(filename: str) -> str:
    if "." not in filename:
        raise ValidationException("File must have an extension")
    return filename.rsplit(".", 1)[-1].lower()


async def create_document(
    db: AsyncSession,
    current_user: User,
    file: UploadFile,
) -> Document:
    """Validate, store, and record a newly uploaded document."""
    extension = _get_extension(file.filename)
    if extension not in ALLOWED_EXTENSIONS:
        raise ValidationException(
            f"File type '.{extension}' is not supported. Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    file_bytes = await file.read()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise ValidationException(f"File exceeds maximum size of {settings.max_upload_size_mb}MB")

    document = Document(
        organization_id=current_user.organization_id,
        uploaded_by_id=current_user.id,
        title=file.filename,
        file_type=extension,
        status="processing",
    )
    db.add(document)
    await db.flush()

    file_key = build_file_key(current_user.organization_id, file.filename)
    upload_file(file_key, file_bytes, file.content_type or "application/octet-stream")

    try:
        extracted_text = extract_text_from_file(extension, file_bytes)
        document.extracted_text = extracted_text
        document.status = "indexed"
    except Exception:
        document.status = "failed"
        extracted_text = None

    version = DocumentVersion(
        document_id=document.id,
        version_number=1,
        file_key=file_key,
        file_size_bytes=len(file_bytes),
        original_filename=file.filename,
    )
    db.add(version)

    if extracted_text:
        from app.ai.ingestion_pipeline import ingest_document_text

        try:
            ingest_document_text(
                organization_id=current_user.organization_id,
                document_id=document.id,
                document_title=file.filename,
                extracted_text=extracted_text,
            )
        except Exception:
            logger.exception("Vector ingestion failed for document %s", document.id)
            document.status = "failed"

    await db.commit()
    await db.refresh(document)
    return document


async def list_documents(
    db: AsyncSession,
    organization_id: uuid.UUID,
    page: int = 1,
    page_size: int = 20,
) -> tuple[list[Document], int]:
    """Return a paginated list of non-deleted documents for an organization."""
    base_query = select(Document).where(
        Document.organization_id == organization_id,
        Document.is_deleted.is_(False),
    )

    count_query = select(func.count()).select_from(base_query.subquery())
    total = (await db.execute(count_query)).scalar_one()

    paginated_query = (
        base_query.order_by(Document.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(paginated_query)
    documents = list(result.scalars().all())

    return documents, total


async def get_document(db: AsyncSession, organization_id: uuid.UUID, document_id: uuid.UUID) -> Document:
    """Retrieve a single document, scoped to the requesting organization."""
    result = await db.execute(
        select(Document).where(
            Document.id == document_id,
            Document.organization_id == organization_id,
            Document.is_deleted.is_(False),
        )
    )
    document = result.scalar_one_or_none()
    if document is None:
        raise NotFoundException("Document not found")
    return document


async def soft_delete_document(db: AsyncSession, organization_id: uuid.UUID, document_id: uuid.UUID) -> None:
    """Mark a document as deleted without removing its underlying data."""
    document = await get_document(db, organization_id, document_id)
    document.is_deleted = True
    await db.commit()