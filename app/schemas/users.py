from pydantic import BaseModel, EmailStr, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    password: str
    phone: str

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "email": "user@example.com",
                "username": "johndoe",
                "password": "strongpass123",
                "phone": "1234567890",
            }
        }
    )


class UserUpdate(BaseModel):
    password: Optional[str] = None


class UserResponse(UserBase):
    id: UUID
    phone: str
    created_at: datetime

    class ConfigDict:
        from_attributes = True


class UserList(BaseModel):
    total: int
    items: list[UserResponse]
