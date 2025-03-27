from datetime import datetime, timedelta, UTC
import os
import secrets
import logging
from jose import jwt
from passlib.context import CryptContext
from fastapi import Response
from app.core.redis import RedisSingleton
from dotenv import load_dotenv
from cryptography.fernet import Fernet
load_dotenv()

logger = logging.getLogger(__name__)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

cipher = Fernet(os.getenv("ENCRYPTION_KEY"))
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 300))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 30))
CSRF_TOKEN_EXPIRE_MINUTES = int(os.getenv("CSRF_TOKEN_EXPIRE_MINUTES", 60))
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


def verify_password(plain_password, hashed_password):
    """Проверка пароля."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    """Хеширование пароля."""
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    """Создание access-токена."""
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Создание refresh-токена."""
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def create_csrf_token() -> str:
    """Создание CSRF-токена."""
    return secrets.token_urlsafe(32)


def set_token_cookie(
        response: Response,
        access_token: str,
        refresh_token: str,
        csrf_token: str
):
    """Установка токенов в куки."""
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )
    response.set_cookie(
        key="csrf_token",
        value=csrf_token,
        httponly=False,
        secure=False,
        samesite="lax",
        max_age=CSRF_TOKEN_EXPIRE_MINUTES * 60,
    )


async def blacklist_token(token: str, expires: int):
    """Добавление токена в чёрный список."""
    try:
        client = await RedisSingleton().redis_client
        if not client:
            raise Exception("Redis client is not initialized")
        await client.setex(token, expires, "blacklisted")
    except Exception as e:
        logger.error(f"Ошибка добавления токена в чёрный список: {e}")
        raise


async def is_token_blacklisted(token: str) -> bool:
    """Проверка, находится ли токен в чёрном списке."""
    redis_client = await RedisSingleton().redis_client
    return await redis_client.exists(token) == 1


async def create_and_store_tokens(user_data: dict, response: Response) -> dict:
    """Генерация и установка всех токенов."""
    access_token = create_access_token(user_data)
    refresh_token = create_refresh_token(user_data)
    csrf_token = create_csrf_token()
    set_token_cookie(response, access_token, refresh_token, csrf_token)
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "csrf_token": csrf_token,
    }
