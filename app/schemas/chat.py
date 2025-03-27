from uuid import UUID

from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MessageBase(BaseModel):
    content: str
    file_url: Optional[str] = None

class MessageCreate(MessageBase):
    pass

class MessageOut(MessageBase):
    id: int
    chat_id: int
    sender_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

class ChatOut(BaseModel):
    id: int
    customer_id: UUID
    performer_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
        