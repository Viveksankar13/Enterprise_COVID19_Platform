from typing import Optional
from pydantic import BaseModel, EmailStr, UUID4
from datetime import datetime


class RoleOut(BaseModel):
    role_id: int
    name: str
    description: Optional[str] = None
    is_active: bool

    class Config:
        from_attributes = True


class UserOut(BaseModel):
    user_id: UUID4
    email: str
    username: str
    full_name: Optional[str] = None
    role: RoleOut
    is_active: bool
    is_verified: bool
    login_count: int
    last_login_at: Optional[datetime] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserOut
