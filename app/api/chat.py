from fastapi import (
    Depends,
    HTTPException,
    status,
    UploadFile,
    File,
)
from sqlalchemy import select
from uuid import UUID
from typing import List
from app.api.storage import upload_file
from app.core.redis import RedisSingleton
from app.core.security import cipher
from app.models.chat import Chat, Message
from app.models.users import Users
from app.schemas.chat import ChatOut, MessageOut
from app.api.auth import get_current_user
from app.api.base import BaseApi
from dotenv import load_dotenv

load_dotenv()


class ChatApi(BaseApi):
    def __init__(self):
        super().__init__()
        self.router.add_api_route(
            "",
            self.create_chat,
            methods=["POST"],
            response_model=ChatOut,
            status_code=status.HTTP_201_CREATED,
        )
        self.router.add_api_route(
            "",
            self.get_chats,
            methods=["GET"],
            response_model=List[ChatOut],
        )
        self.router.add_api_route(
            "/{chat_id}/messages",
            self.get_messages,
            methods=["GET"],
            response_model=List[MessageOut],
        )
        self.router.add_api_route(
            "/upload-file",
            self.upload_chat_file,
            methods=["POST"],
            response_model=dict,
        )
        self.redis_client = RedisSingleton().redis_client

    async def create_chat(
        self,
        customer_id: UUID,
        performer_id: UUID,
        current_user: Users = Depends(get_current_user),
    ) -> ChatOut:
        """
        Создание нового чата между заказчиком и исполнителем.
        Args:
            customer_id: UUID заказчика
            performer_id: UUID исполнителя
            current_user: Авторизованный пользователь
        Returns:
            ChatOut: Созданный чат
        Raises:
            HTTPException: Если пользователь не имеет прав или участники не найдены
        """
        if current_user.id not in [customer_id, performer_id]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can only create a chat if "
                "you are a customer or performer",
            )
        async with self.db as db:
            customer = await db.execute(select(Users).where(Users.id == customer_id))
            customer = customer.scalars().first()
            if not customer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Customer not found",
                )
            performer = await db.execute(select(Users).where(Users.id == performer_id))
            performer = performer.scalars().first()
            if not performer:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Performer not found",
                )
            existing_chat = await db.execute(
                select(Chat).where(
                    (Chat.customer_id == customer_id)
                    & (Chat.performer_id == performer_id)
                )
            )
            existing_chat = existing_chat.scalars().first()
            if existing_chat:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Chat between these users already exists",
                )
            chat = Chat(customer_id=customer_id, performer_id=performer_id)
            db.add(chat)
            await self.update_db(db, chat)
        return chat

    async def get_chats(
        self,
        current_user: Users = Depends(get_current_user),
    ) -> List[ChatOut]:
        """
        Получение списка чатов текущего пользователя.
        Args:
            current_user: Авторизованный пользователь
        Returns:
            List[ChatOut]: Список чатов
        """
        async with self.db as db:
            chats = await db.execute(
                select(Chat).where(
                    (Chat.customer_id == current_user.id)
                    | (Chat.performer_id == current_user.id)
                )
            )
            chats = chats.scalars().all()
        return chats

    async def get_messages(
        self,
        chat_id: int,
        skip: int = 0,
        limit: int = 50,
        current_user: Users = Depends(get_current_user),
    ) -> List[MessageOut]:
        """
        Получение сообщений в чате с пагинацией.
        Args:
            chat_id: UUID чата
            skip: Пропуск записей
            limit: Лимит записей
            current_user: Авторизованный пользователь

        Returns:
            List[MessageOut]: Список сообщений
        Raises:
            HTTPException: Если чат не найден или пользователь не имеет доступа
        """
        async with self.db as db:
            chat = await db.execute(select(Chat).where(Chat.id == chat_id))
            chat = chat.scalars().first()
            if not chat:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Chat not found",
                )

            if current_user.id not in [chat.customer_id, chat.performer_id]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You do not have access to this chat",
                )

            messages = await db.execute(
                select(Message)
                .where(Message.chat_id == chat_id)
                .offset(skip)
                .limit(limit)
            )
            messages = messages.scalars().all()
        for msg in messages:
            try:
                msg.content = cipher.decrypt(msg.content.encode()).decode()
            except Exception:
                msg.content = "Ошибка расшифровки"
        return messages

    async def upload_chat_file(
        self,
        file: UploadFile = File(...),
        current_user: Users = Depends(get_current_user),
    ) -> dict:
        """
        Загрузка файла для чата.
        Args:
            file: Загружаемый файл
            current_user: Авторизованный пользователь
        Returns:
            dict: Ссылка на загруженный файл
        """
        file_url = await upload_file(file)
        return {"file_url": file_url}
