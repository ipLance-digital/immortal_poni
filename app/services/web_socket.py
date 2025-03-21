import json
from uuid import UUID

from fastapi import Depends, HTTPException
from sqlalchemy import select
from starlette import status
from starlette.websockets import WebSocket, WebSocketDisconnect

from app.api.auth import get_current_user
from app.main import router
from app.models.chat import Chat, Message
from app.models.users import Users
from app.schemas.chat import MessageOut

@router.websocket("/ws/{chat_id}")
async def websocket_endpoint(
    self,
    websocket: WebSocket,
    chat_id: UUID,
    current_user: Users = Depends(get_current_user)
):
    """
    WebSocket эндпоинт для реального общения в чате.
    Проверка прав пользователя перед подключением.
    """
    await websocket.accept()
    async with self.db as db:
        chat = await db.execute(select(Chat).where(Chat.id == chat_id))
        chat = chat.scalars().first()

        if not chat:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Чат не найден")

        # Проверка прав доступа
        if current_user.id not in [chat.customer_id, chat.performer_id]:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="У вас нет доступа к этому чату")

    try:
        while True:
            data = await websocket.receive_text()
            message = Message(
                chat_id=chat_id,
                sender_id=current_user.id,
                content=data
            )
            async with self.db as db:
                db.add(message)
                await self.update_db(db, message)
            message_out = MessageOut(id=message.id, sender_id=current_user.id, content=message.content)
            await websocket.send_text(json.dumps(message_out.dict()))
            await self.redis_client.set(f"chat:{chat_id}:message:{message.id}", json.dumps(message_out.dict()))

    except WebSocketDisconnect:
        print(f"Пользователь {current_user.id} отключился от чата {chat_id}")
        await websocket.close()