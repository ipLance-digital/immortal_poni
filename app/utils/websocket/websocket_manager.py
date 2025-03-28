from typing import List, Dict
from uuid import UUID
from sqlalchemy import func
from fastapi import WebSocket
from jose import JWTError, jwt
from sqlalchemy.future import select

from app.core.database import PgSingleton
from app.models.users import Users
import os


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[UUID, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, user_id):
        """Добавляет WebSocket подключение для конкретного пользователя."""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = []
        self.active_connections[user_id].append(websocket)

    async def disconnect(self, websocket: WebSocket, user_id):
        """Удаляет WebSocket подключение для конкретного пользователя."""
        if user_id in self.active_connections:
            self.active_connections[user_id].remove(websocket)
            if not self.active_connections[user_id]:
                del self.active_connections[user_id]

    async def broadcast(self, message: str):
        """Отправляет сообщение всем активным подключениям."""
        for user_connections in self.active_connections.values():
            for connection in user_connections:
                await connection.send_text(message)

    async def send_personal_message(self, message: str, user_id):
        """Отправляет сообщение конкретному пользователю, если он подключен."""
        if user_id in self.active_connections:
            for connection in self.active_connections[user_id]:
                await connection.send_text(message)
        else:
            # TODO нужны варианты доставки сообщения, если пользователь вне чата
            pass


async def get_current_user_websocket(access_token) -> Users | None:
    if not access_token:
        await ConnectionManager().broadcast("access_token not was response")
    try:
        payload = jwt.decode(
            access_token,
            os.getenv("SECRET_KEY"),
            algorithms=[os.getenv("ALGORITHM")],
        )
        username: str = payload.get("sub")
        if username is None:
            await ConnectionManager().broadcast("access_token not was response")

        async with PgSingleton().session as db:
            user = await db.execute(
                select(Users).where(func.lower(Users.username) == username.lower())
            )
            user = user.scalars().first()
            if user is None:
                await ConnectionManager().broadcast("access_token not was response")
            return user

    except JWTError:
        await ConnectionManager().broadcast("access_token not was response")
