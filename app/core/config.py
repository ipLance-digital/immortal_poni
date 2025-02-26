"""
Модуль конфигурации приложения.
Содержит все настройки, загружаемые из переменных окружения.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    """
    Настройки приложения, загружаемые из .env файла.

    Attributes:
        APP_NAME: Название приложения
        DEBUG: Режим отладки
        API_V1_STR: Префикс для API v1
        LOCALHOST: Хост для запуска сервера
        PORT: Порт для запуска сервера
        SECRET_KEY: Секретный ключ для JWT токенов
        ALGORITHM: Алгоритм для JWT токенов
        ACCESS_TOKEN_EXPIRE_MINUTES: Время жизни JWT токена
        DATABASE_URL: URL для подключения к базе данных
        DB_POOL_SIZE: Размер пула подключений к БД
        DB_MAX_OVERFLOW: Максимальное количество дополнительных подключений
    """

    # Общие настройки
    APP_NAME: str = "IP-lance API"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # Настройки сервера
    LOCALHOST: str = "0.0.0.0"
    PORT: int = 8000

    # Настройки JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "dev-secret-key-not-for-production")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # База данных
    DATABASE_URL: str = os.getenv("DATABASE_URL")
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_PASSWORD: str | None = None
    PYTHONPATH: str | None = None

    # Хранилище
    SUPABASE_URL: str = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: str = os.getenv("SUPABASE_SERVICE_KEY")
    BUCKET_NAME: str = os.getenv("BUCKET_NAME")

    class Config:
        env_file = ".env"
        extra = "allow"


@lru_cache()
def get_settings() -> Settings:
    """
    Получение настроек приложения с кэшированием.

    Returns:
        Settings: Объект с настройками приложения
    """
    return Settings()


settings = get_settings()
