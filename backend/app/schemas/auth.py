import uuid
from typing import List, Optional
from pydantic import BaseModel, EmailStr, Field

class Token(BaseModel):
    """Schema returned upon successful authentication."""
    access_token: str = Field(..., description="JWT access token.")
    refresh_token: str = Field(..., description="JWT refresh token.")
    token_type: str = Field(default="bearer", description="Token type designation.")

class TokenPayload(BaseModel):
    """Schema decoded from valid JWT token payloads."""
    sub: Optional[str] = Field(default=None, description="Subject (User ID).")
    jti: Optional[str] = Field(default=None, description="Unique token JWT ID.")
    exp: Optional[int] = Field(default=None, description="Expiry timestamp.")
    permissions: List[str] = Field(default_factory=list, description="List of user permissions.")
    role: Optional[str] = Field(default=None, description="User role name.")

class LoginRequest(BaseModel):
    """Payload representing login credential checks."""
    email: EmailStr = Field(..., description="User login email.")
    password: str = Field(..., description="User login password.")

class RefreshRequest(BaseModel):
    """Payload representing token rotation validation checks."""
    refresh_token: str = Field(..., description="Valid refresh token.")
