import uuid
from typing import List
from datetime import datetime
from app.models.base_model import Base
from sqlalchemy import (
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    func,
    Table,
    Column,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)


user_skills_connector = Table(
    "user_skills_connector",
    Base.metadata,
    Column("user_id", UUID, ForeignKey("users.id"), primary_key=True),
    Column("skill_id", Integer, ForeignKey("user_skills.id"), primary_key=True),
)

user_review_connector = Table(
    "user_review_connector",
    Base.metadata,
    Column("user_id", UUID, ForeignKey("users.id"), primary_key=True),
    Column("review_id", Integer, ForeignKey("reviews.id"), primary_key=True),
)


class Users(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    fio: Mapped[str] = mapped_column(String, nullable=True)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    phone: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    telegram_id: Mapped[str] = mapped_column(String, unique=True, nullable=True)
    last_activity: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)

    skills: Mapped[List["UserSkills"]] = relationship(
        "UserSkills", secondary=user_skills_connector, back_populates="users"
    )
    reviews: Mapped[List["Review"]] = relationship(
        "Review", secondary=user_review_connector, back_populates="users"
    )
    orders_created = relationship(
        "Order", foreign_keys="Order.created_by", back_populates="creator"
    )
    orders_assigned = relationship(
        "Order", foreign_keys="Order.assign_to", back_populates="assignee"
    )
    chats = relationship(
        "Chat", secondary="chat_participants", back_populates="participants"
    )


class UserSkills(Base):
    __tablename__ = "user_skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)

    users: Mapped[List["Users"]] = relationship(
        "Users",
        secondary=user_skills_connector,
        back_populates="skills",
    )


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String, nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    users: Mapped[List["Users"]] = relationship(
        "Users", secondary=user_review_connector, back_populates="reviews"
    )


from app.models.orders import Order
