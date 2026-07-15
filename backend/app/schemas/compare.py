import uuid

from pydantic import BaseModel


class CompareRequest(BaseModel):
    document_id_a: uuid.UUID
    document_id_b: uuid.UUID


class CompareResponse(BaseModel):
    comparison: str
    document_title_a: str
    document_title_b: str