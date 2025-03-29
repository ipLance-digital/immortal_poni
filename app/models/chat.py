import uuid
from sqlalchemy import Integer, String, Boolean, ForeignKey, DateTime, UUID
from sqlalchemy.orm import relationship, Mapped, mapped_column
from datetime import datetime
from app.models.base_model import Base


class Chat(Base):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    customer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    performer_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    is_group: Mapped[bool] = mapped_column(Boolean, default=False)

    customer = relationship("Users", foreign_keys=[customer_id])
    performer = relationship("Users", foreign_keys=[performer_id])
    messages = relationship("Message", back_populates="chat")

    participants = relationship(
        "Users", secondary="chat_participants", back_populates="chats"
    )
    attachments = relationship(
        "ChatAttachment", back_populates="chat", cascade="all, delete-orphan"
    )


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"))
    sender_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    content: Mapped[str] = mapped_column(String, nullable=False)
    file_url: Mapped[str] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    chat = relationship("Chat", back_populates="messages")
    sender = relationship("Users")


class ChatParticipant(Base):
    __tablename__ = "chat_participants"

    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"), primary_key=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), primary_key=True)


class ChatAttachment(Base):
    __tablename__ = "chat_attachments"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), default=uuid.uuid4, primary_key=True
    )
    chat_id: Mapped[int] = mapped_column(
        ForeignKey("chats.id"), nullable=False
    )
    file_id: Mapped[str] = mapped_column(String, nullable=False)
    chat = relationship("Chat", back_populates="attachments")