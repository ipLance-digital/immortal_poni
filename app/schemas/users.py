"""
Модуль схем пользователя.
Содержит Pydantic модели для валидации данных пользователя.
"""

from pydantic import BaseModel, EmailStr, Field
from uuid import UUID
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    """
    Базовая схема пользователя.

    Attributes:
        email (EmailStr): Email пользователя
        username (str): Имя пользователя
    """

    email: EmailStr
    username: str


class UserCreate(UserBase):
    """
    Схема создания пользователя.

    Attributes:
        email (EmailStr): Email пользователя
        username (str): Имя пользователя
        password (str): Пароль (минимум 8 символов)
    """

    email: EmailStr = Field(..., example="user@example.com")
    username: str = Field(..., example="johndoe")
    password: str = Field(..., min_length=8, example="strongpass123")
    phone: int = Field(..., example=1234567890)
    telegram_id: str = Field(..., example="1234567890")


class UserUpdate(BaseModel):
    """
    Схема обновления пользователя.
    Все поля опциональны.

    Attributes:
        email (EmailStr, optional): Новый email
        username (str, optional): Новое имя пользователя
        password (str, optional): Новый пароль
        is_active (bool, optional): Статус активности
    """

    email: Optional[EmailStr] = None
    username: Optional[str] = None
    password: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """
    Схема ответа с данными пользователя.

    Attributes:
        id (UUID): Уникальный идентификатор
        email (EmailStr): Email пользователя
        username (str): Имя пользователя
        created_at (datetime): Дата и время создания
    """

    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True


class UserList(BaseModel):
    """
    Схема списка пользователей.

    Attributes:
        total (int): Общее количество пользователей
        items (list[UserResponse]): Список пользователей
    """

    total: int
    items: list[UserResponse]
