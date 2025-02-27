"""
Модуль маршрутизации.
Объединяет все роутеры приложения в единый маршрутизатор.
"""

from fastapi import APIRouter
from app.api import users, auth, storage

def get_router() -> APIRouter:
    """
    Создает и настраивает основной роутер приложения.

    Returns:
        APIRouter: Сконфигурированный роутер со всеми подключенными эндпоинтами.

    Note:
        Подключает роутеры:
        - auth: Аутентификация и авторизация (/auth/*)
        - users: Управление пользователями (/users/*)
        - storage: Управление файлами в Supabase Storage (/storage/*)
    """
    router = APIRouter()

    router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
    router.include_router(users.router, prefix="/users", tags=["Users"])
    router.include_router(storage.router, prefix="/storage", tags=["Storage"])  

    return router