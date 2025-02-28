from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    email: EmailStr = Field(..., example="user@example.com", nullable=True)
    username: str = Field(..., example="johndoe", nullable=True)
    password: str = Field(..., min_length=8, example="strongpass123", nullable=True)
    phone: str = Field(..., example="1234567890", nullable=True)


class UserUpdate(BaseModel):
    password: Optional[str] = None


class UserResponse(UserBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class UserList(BaseModel):
    total: int
    items: list[UserResponse]
