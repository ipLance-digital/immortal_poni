import asyncio
from celery import shared_task
from app.core.database import PgSingleton
from app.models.chat import Chat
from app.models.users import Users
from sqlalchemy import select


async def async_send_notification(chat_id: str, message_content: str):
    async with PgSingleton().session as db:
        chat = (
            (await db.execute(select(Chat).where(Chat.id == chat_id))).scalars().first()
        )
        if not chat:
            print(f"Chat {chat_id} not found")
            return

        customer = (
            (await db.execute(select(Users).where(Users.id == chat.customer_id)))
            .scalars()
            .first()
        )
        performer = (
            (await db.execute(select(Users).where(Users.id == chat.performer_id)))
            .scalars()
            .first()
        )

        if not customer or not performer:
            print("Customer or performer not found")
            return

        print(
            f"Notification to {customer.email}:"
            f" New message in chat {chat_id}: {message_content}"
        )
        print(
            f"Notification to {performer.email}:"
            f" New message in chat {chat_id}: {message_content}"
        )


@shared_task
def send_notification(chat_id: str, message_content: str):
    asyncio.run(async_send_notification(chat_id, message_content))
