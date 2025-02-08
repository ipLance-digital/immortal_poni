"""
Модуль моделей базы данных.
Содержит SQLAlchemy модели для работы с таблицами.
"""
from sqlalchemy import Boolean, Column, Integer, String, DateTime, UUID
from sqlalchemy.sql import func
from app.database import Base
from uuid import uuid4

class User(Base):
    """
    Модель пользователя.
    
    Attributes:
        id (UUID): Уникальный идентификатор пользователя
        email (str): Email пользователя (уникальный)
        username (str): Имя пользователя (уникальное)
        hashed_password (str): Хешированный пароль
        is_active (bool): Статус активности пользователя
        created_at (datetime): Дата и время создания
    """
    __tablename__ = "users"

    id = Column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid4,
        index=True
    )
    email = Column(
        String, 
        unique=True, 
        index=True,
        nullable=False
    )
    username = Column(
        String, 
        unique=True, 
        index=True,
        nullable=False
    )
    hashed_password = Column(
        String,
        nullable=False
    )
    is_active = Column(
        Boolean, 
        default=True
    )
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
