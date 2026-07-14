import uuid

from pydantic import BaseModel, EmailStr, Field


class UserProfileResponse(BaseModel):
    id: uuid.UUID
    email: EmailStr
    full_name: str
    role: str
    is_active: bool

    model_config = {"from_attributes": True}


class UserProfileUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None, min_length=1, max_length=255)


class DeactivateAccountRequest(BaseModel):
    confirm: bool = Field(description="Must be true to confirm deactivation")