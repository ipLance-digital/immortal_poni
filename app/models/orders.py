import uuid
from datetime import datetime
from app.models.base_model import Base
from app.models.users import Users
from sqlalchemy import (
    Integer,
    String,
    ForeignKey,
    DateTime,
    func,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.users import Users


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), default=uuid.uuid4, primary_key=True
    )
    name: Mapped[str] = mapped_column(String(100), unique=False, nullable=False)
    body: Mapped[str] = mapped_column(String, unique=False, nullable=False)
    price: Mapped[int] = mapped_column(Integer, unique=False, nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, unique=False, nullable=False, server_default=func.now()
    )
    status_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("order_statuses.id"), unique=False, nullable=False
    )
    assign_to: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    deadline: Mapped[datetime] = mapped_column(DateTime, unique=False, nullable=True)
    attachments: Mapped[str] = mapped_column(String, unique=False, nullable=True)

    user: Mapped["Users"] = relationship("Users", back_populates="user")
    status: Mapped["OrderStatus"] = relationship("OrderStatus", back_populates="status")


class OrderStatus(Base):
    __tablename__ = "order_statuses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)
