from pydantic_settings import BaseSettings
import os
from dotenv import load_dotenv
load_dotenv()


class Settings(BaseSettings):
    # Общие настройки
    APP_NAME: str = "IP-lance API"
    DEBUG: bool = True
    API_V1_STR: str = "/api/v1"

    # Настройки сервера
    LOCALHOST: str = "0.0.0.0"
    PORT: int = 8000

    # Настройки JWT
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "dev-secret-key-not-for-production"
    )
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

    # Celery
    CELERY_BROKER_URL: str = "redis://localhost:6379/0"
    CELERY_RESULT_BACKEND: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"
        extra = "allow"
