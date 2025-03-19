from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Text, \
    Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.models.base_model import Base


class Chat(Base):
    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    performer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_group = Column(Boolean, default=False)
    customer = relationship("Users", foreign_keys=[customer_id])
    performer = relationship("Users", foreign_keys=[performer_id])
    messages = relationship("Message", back_populates="chat")

    participants = relationship(
        "Users",
        secondary="chat_participants",
        back_populates="chats"
    )


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id"))
    sender_id = Column(Integer, ForeignKey("users.id"))
    content = Column(Text, nullable=False)
    file_url = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    chat = relationship("Chat", back_populates="messages")
    sender = relationship("Users")


class ChatParticipant(Base):
    __tablename__ = "chat_participants"

    chat_id = Column(Integer, ForeignKey("chats.id"), primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), primary_key=True)
    chat = relationship("Chat", back_populates="participants")
    user = relationship("Users", back_populates="chats")