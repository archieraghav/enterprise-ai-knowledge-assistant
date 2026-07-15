import uuid
from datetime import datetime

from pydantic import BaseModel, EmailStr


class AdminUserResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str
    role: str
    is_active: bool
    is_superuser: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminUserListResponse(BaseModel):
    items: list[AdminUserResponse]
    total: int


class UpdateUserRoleRequest(BaseModel):
    role: str


class OrganizationMetricsResponse(BaseModel):
    total_users: int
    active_users: int
    total_documents: int
    indexed_documents: int
    failed_documents: int
    total_conversations: int