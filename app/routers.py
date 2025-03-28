from fastapi import APIRouter
from app.api.chat import ChatApi
from app.api.users import UsersApi
from app.api.orders import OrdersApi
from app.api.auth import AuthApi


def get_router() -> APIRouter:
    """
    Создает и настраивает основной роутер приложения.

    Returns:
        APIRouter: Сконфигурированный роутер со всеми подключенными эндпоинтами.

    Note:
        Подключает роутеры:
        - auth: Аутентификация и авторизация (/auth/*)
        - users: Управление пользователями (/users/*)
    """
    router = APIRouter()
    users = UsersApi()
    orders = OrdersApi()
    chats = ChatApi()
    auth = AuthApi()

    router.include_router(auth.router, prefix=auth.prefix, tags=auth.tags)
    router.include_router(users.router, prefix=users.prefix, tags=users.tags)
    router.include_router(orders.router, prefix=orders.prefix, tags=orders.tags)
    router.include_router(chats.router, prefix=chats.prefix, tags=chats.tags)

    return router
