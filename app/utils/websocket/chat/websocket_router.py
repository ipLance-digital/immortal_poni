from app.core.database import PgSingleton
from app.utils.websocket.chat.services import validate_chat_and_user, save_message
from app.utils.websocket.websocket_manager import (
    ConnectionManager,
    get_current_user_websocket
)
from app.routers import router
from fastapi import (
    WebSocket,
    WebSocketDisconnect
)

manager = ConnectionManager()

@router.websocket("/ws/chat/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, token: str, chat_id: int):
    try:
        async with PgSingleton().session as db:
            user = await get_current_user_websocket(token)
            if user:
                chat = await validate_chat_and_user(db, chat_id, user.id)
                await manager.connect(websocket, user.id)
                await manager.broadcast(f"Пользователь {user.username} присоединился к чату.")
                while True:
                    data = await websocket.receive_text()
                    if data:
                        message = await save_message(db, chat.id, user.id, data)
                        await manager.broadcast(f"Сообщение: {message.content}")

    except ValueError as e:
        await manager.broadcast(str(e))
        await manager.disconnect(websocket, user.id)

    except WebSocketDisconnect:
        await manager.disconnect(websocket, user.id)
        await manager.broadcast(f"Пользователь {user.username} покинул чат.")
