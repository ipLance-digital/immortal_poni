import uuid

from typing import List

from sqlalchemy import (
    Integer,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import expression
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from datetime import datetime
from app.database import Base


class Users(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    fio: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    username: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    phone: Mapped[int] = mapped_column(Integer, unique=True, nullable=False)
    telegram_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    last_activity: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    is_verified: Mapped[bool] = mapped_column(
        Boolean, server_default=expression.false()
    )

    skill_connectors: Mapped[List["UserSkillConnector"]] = relationship(
        "UserSkillConnector", back_populates="user"
    )
    skills = relationship(
        "UserSkills", secondary="user_skills_connector", back_populates="users"
    )

    review_connectors = relationship(
        "UserReviewConnector", back_populates="user", cascade="all, delete-orphan"
    )
    reviews = relationship(
        "Review", secondary="user_reviews_connector", back_populates="users"
    )


class UserSkills(Base):
    __tablename__ = "user_skills"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, nullable=False, index=True)

    users: Mapped[List["Users"]] = relationship(
        "User",
        secondary="user_skills_connector",
        primaryjoin="UserSkills.id == UserSkillConnector.skill_id",
        secondaryjoin="User.id == UserSkillConnector.user_id",
        back_populates="skills",
    )


class UserSkillConnector(Base):
    __tablename__ = "user_skills_connector"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    skill_id: Mapped[int] = mapped_column(
        ForeignKey("user_skills.id"), nullable=False, index=True
    )

    user: Mapped["Users"] = relationship("User", back_populates="skill_connectors")
    skill: Mapped["UserSkills"] = relationship("UserSkills")


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    text: Mapped[str] = mapped_column(String, nullable=False)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    users = relationship("UserReviewConnector", back_populates="review")


class UserReviewConnector(Base):
    __tablename__ = "user_reviews_connector"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"), nullable=False, index=True
    )
    review_id: Mapped[int] = mapped_column(
        ForeignKey("reviews.id"), nullable=False, index=True
    )

    user: Mapped["Users"] = relationship("User", back_populates="skill_connectors")
    review: Mapped["Review"] = relationship("Review")
