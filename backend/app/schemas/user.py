import uuid
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

class PermissionOut(BaseModel):
    """Schema representing permission records."""
    id: uuid.UUID
    name: str
    description: Optional[str] = None

    class Config:
        from_attributes = True

class RoleOut(BaseModel):
    """Schema representing role records."""
    id: uuid.UUID
    name: str
    description: Optional[str] = None
    permissions: List[PermissionOut] = []

    class Config:
        from_attributes = True

class UserOut(BaseModel):
    """Schema representing user details."""
    id: uuid.UUID
    email: EmailStr
    is_active: bool
    role: RoleOut
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserCreate(BaseModel):
    """Schema payload representing user registration."""
    email: EmailStr
    password: str = Field(..., min_length=8, description="Must be at least 8 characters.")
    role_id: uuid.UUID

class UserUpdate(BaseModel):
    """Schema payload representing user detail updates."""
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=8, description="Must be at least 8 characters.")
    role_id: Optional[uuid.UUID] = None
    is_active: Optional[bool] = None

class RoleCreate(BaseModel):
    """Schema payload representing new system role creation."""
    name: str
    description: Optional[str] = None
    permission_ids: List[uuid.UUID] = []
