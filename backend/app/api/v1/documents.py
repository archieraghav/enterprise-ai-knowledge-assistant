import uuid

from fastapi import APIRouter, Depends, File, Query, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.document_version import DocumentVersionResponse, VersionHistoryResponse
from app.services.versioning_service import create_new_version, get_version_history


from app.api.dependencies import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.document import DocumentListResponse, DocumentResponse
from app.services.document_service import (
    create_document,
    get_document,
    list_documents,
    soft_delete_document,
)

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentResponse:
    document = await create_document(db, current_user, file)
    return DocumentResponse.model_validate(document)


@router.get("", response_model=DocumentListResponse)
async def get_documents(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentListResponse:
    documents, total = await list_documents(db, current_user.organization_id, page, page_size)
    return DocumentListResponse(
        items=[DocumentResponse.model_validate(doc) for doc in documents],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document_detail(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentResponse:
    document = await get_document(db, current_user.organization_id, document_id)
    return DocumentResponse.model_validate(document)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> None:
    await soft_delete_document(db, current_user.organization_id, document_id)



@router.post("/{document_id}/versions", response_model=DocumentVersionResponse, status_code=status.HTTP_201_CREATED)
async def upload_new_version(
    document_id: uuid.UUID,
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> DocumentVersionResponse:
    version = await create_new_version(db, current_user.organization_id, document_id, file)
    return DocumentVersionResponse.model_validate(version)


@router.get("/{document_id}/versions", response_model=VersionHistoryResponse)
async def get_document_versions(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
) -> VersionHistoryResponse:
    versions = await get_version_history(db, current_user.organization_id, document_id)
    return VersionHistoryResponse(
        document_id=document_id,
        versions=[DocumentVersionResponse.model_validate(v) for v in versions],
    )