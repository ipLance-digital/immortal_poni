import datetime

from sqlalchemy import select
from app.models.chat import Chat, Message
from app.api.base import BaseApi


async def validate_chat_and_user(db, chat_id: int, user_id) -> Chat:
    """
    Проверяет существование чата и принадлежность пользователя к чату.
    """
    chat = await db.execute(select(Chat).where(Chat.id == chat_id))
    chat = chat.scalars().first()
    if not chat:
        raise ValueError("Чат не найден.")
    if user_id not in [chat.customer_id, chat.performer_id]:
        raise ValueError("Пользователь не найден.")
    return chat


async def save_message(db, chat_id: int, sender_id, content: str) -> Message:
    """
    Сохраняет сообщение в базе данных.
    """
    encrypted_content = BaseApi.security.cipher.encrypt(content.encode()).decode()
    message = Message(
        chat_id=chat_id,
        sender_id=sender_id,
        content=encrypted_content,
        created_at=datetime.datetime.utcnow(),
    )
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message
