from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID
import uuid
from app.database import Base
from sqlalchemy import (
    Boolean, 
    Column, 
    Integer, 
    String, 
    DateTime,
)

class Users(Base):
    __tablename__ = "users"
    id = Column(
        UUID(as_uuid=True),
        primary_key=True, 
        default=uuid.uuid4
    )
    email = Column(
        String, 
        unique=True, 
        index=True
    )
    username = Column(
        String, 
        unique=True, 
        index=True
    )
    hashed_password = Column(
        String
    )
    is_active = Column(
        Boolean, 
        default=True
    )
    created_at = Column(
        DateTime(timezone=True), 
        server_default=func.now()
    )
    phone = Column(
        String, 
        unique=True, 
        index=True
    )
    telegram_id = Column(
        String, 
        unique=True, 
        index=True
    )
    is_verified = Column(
        Boolean, 
        default=False
    )
