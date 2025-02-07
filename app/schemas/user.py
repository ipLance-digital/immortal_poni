from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    username: str

class UserCreate(UserBase):
    """
    Схема создания пользователя

    Attributes:
        email: Email пользователя
        username: Уникальное имя пользователя
        password: Пароль (минимум 8 символов)
    """
    email: EmailStr = Field(..., example="user@example.com")
    username: str = Field(..., example="johndoe")
    password: str = Field(..., min_length=8, example="strongpass123")

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None

class UserResponse(UserBase):
    id: UUID
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True

class UserList(BaseModel):
    total: int
    items: list[UserResponse] 