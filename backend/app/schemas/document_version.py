import uuid
from datetime import datetime

from pydantic import BaseModel


class DocumentVersionResponse(BaseModel):
    id: uuid.UUID
    version_number: int
    original_filename: str
    file_size_bytes: int
    created_at: datetime

    model_config = {"from_attributes": True}


class VersionHistoryResponse(BaseModel):
    document_id: uuid.UUID
    versions: list[DocumentVersionResponse]