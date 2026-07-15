import uuid

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import ValidationException
from app.models.document import Document
from app.models.document_version import DocumentVersion
from app.models.user import User
from app.services.storage_service import build_file_key, upload_file

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
        status="uploaded",
    )
    db.add(document)
    await db.flush()

    file_key = build_file_key(current_user.organization_id, file.filename)
    upload_file(file_key, file_bytes, file.content_type or "application/octet-stream")

    version = DocumentVersion(
        document_id=document.id,
        version_number=1,
        file_key=file_key,
        file_size_bytes=len(file_bytes),
        original_filename=file.filename,
    )
    db.add(version)

    await db.commit()
    await db.refresh(document)
    return document