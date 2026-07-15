import uuid

from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ValidationException
from app.models.document import Document
from app.models.document_version import DocumentVersion
from app.services.document_service import _get_extension, ALLOWED_EXTENSIONS
from app.services.document_service import get_document
from app.services.storage_service import build_file_key, upload_file
from app.core.config import settings


async def create_new_version(
    db: AsyncSession,
    organization_id: uuid.UUID,
    document_id: uuid.UUID,
    file: UploadFile,
) -> DocumentVersion:
    """Upload a new file as the next version of an existing document."""
    document = await get_document(db, organization_id, document_id)

    extension = _get_extension(file.filename)
    if extension not in ALLOWED_EXTENSIONS:
        raise ValidationException(
            f"File type '.{extension}' is not supported. Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
        )

    file_bytes = await file.read()
    max_bytes = settings.max_upload_size_mb * 1024 * 1024
    if len(file_bytes) > max_bytes:
        raise ValidationException(f"File exceeds maximum size of {settings.max_upload_size_mb}MB")

    result = await db.execute(
        select(DocumentVersion)
        .where(DocumentVersion.document_id == document.id)
        .order_by(DocumentVersion.version_number.desc())
        .limit(1)
    )
    latest_version = result.scalar_one_or_none()
    next_version_number = (latest_version.version_number + 1) if latest_version else 1

    file_key = build_file_key(organization_id, file.filename)
    upload_file(file_key, file_bytes, file.content_type or "application/octet-stream")

    new_version = DocumentVersion(
        document_id=document.id,
        version_number=next_version_number,
        file_key=file_key,
        file_size_bytes=len(file_bytes),
        original_filename=file.filename,
    )
    db.add(new_version)

    document.file_type = extension
    document.title = file.filename

    await db.commit()
    await db.refresh(new_version)
    return new_version


async def get_version_history(
    db: AsyncSession,
    organization_id: uuid.UUID,
    document_id: uuid.UUID,
) -> list[DocumentVersion]:
    """Return all versions of a document, newest first."""
    # Confirms document exists and belongs to this organization.
    await get_document(db, organization_id, document_id)

    result = await db.execute(
        select(DocumentVersion)
        .where(DocumentVersion.document_id == document_id)
        .order_by(DocumentVersion.version_number.desc())
    )
    return list(result.scalars().all())