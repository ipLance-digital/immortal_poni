import uuid
from datetime import datetime
from app.models.base_model import Base
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


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), default=uuid.uuid4, primary_key=True
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    body: Mapped[str] = mapped_column(String, nullable=False)
    price: Mapped[int] = mapped_column(Integer, nullable=False)
    created_by: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    assign_to: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    status_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("order_statuses.id"), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    deadline: Mapped[datetime] = mapped_column(DateTime, nullable=True)
    attachments = relationship(
        "OrderAttachment", back_populates="order", cascade="all, delete-orphan"
    )
    creator = relationship(
        "Users", back_populates="orders_created", foreign_keys=[created_by]
    )
    assignee = relationship(
        "Users", back_populates="orders_assigned", foreign_keys=[assign_to]
    )
    status = relationship("OrderStatus", back_populates="orders")


class OrderStatus(Base):
    __tablename__ = "order_statuses"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(30), unique=True, nullable=False)

    orders = relationship("Order", back_populates="status")


class OrderAttachment(Base):
    __tablename__ = "order_attachments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), default=uuid.uuid4, primary_key=True
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("orders.id"), nullable=False
    )
    file_id: Mapped[str] = mapped_column(String, nullable=False)

    order = relationship("Order", back_populates="attachments")
