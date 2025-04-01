from datetime import datetime, timedelta, UTC
import os
import secrets
import logging
from jose import jwt
from passlib.context import CryptContext
from fastapi import Response
from app.core.database import RedisSingleton
from cryptography.fernet import Fernet


logger = logging.getLogger(__name__)


class Security:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.cipher = Fernet(os.getenv("ENCRYPTION_KEY"))
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(
            os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 300)
        )
        self.REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 30))
        self.CSRF_TOKEN_EXPIRE_MINUTES = int(os.getenv("CSRF_TOKEN_EXPIRE_MINUTES", 60))
        self.SECRET_KEY = os.getenv("SECRET_KEY")
        self.ALGORITHM = os.getenv("ALGORITHM")
        self.redis = RedisSingleton()

    def verify_password(self, plain_password, hashed_password):
        """Проверка пароля."""
        return self.pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password):
        """Хеширование пароля."""
        return self.pwd_context.hash(password)

    def create_access_token(self, data: dict) -> str:
        """Создание access-токена."""
        to_encode = data.copy()
        expire = datetime.now(UTC) + timedelta(minutes=self.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt

    def create_refresh_token(self, data: dict) -> str:
        """Создание refresh-токена."""
        to_encode = data.copy()
        expire = datetime.now(UTC) + timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALGORITHM)
        return encoded_jwt

    def create_csrf_token(self) -> str:
        """Создание CSRF-токена."""
        return secrets.token_urlsafe(32)

    def set_token_cookie(
        self, response: Response, access_token: str, refresh_token: str, csrf_token: str
    ):
        """Установка токенов в куки."""
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=False,
            secure=False,
            samesite="lax",
            max_age=self.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=False,
            secure=False,
            samesite="lax",
            max_age=self.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
        )
        response.set_cookie(
            key="csrf_token",
            value=csrf_token,
            httponly=False,
            secure=False,
            samesite="lax",
            max_age=self.CSRF_TOKEN_EXPIRE_MINUTES * 60,
        )

    async def blacklist_token(self, token: str, expires: int):
        """Добавление токена в чёрный список."""
        try:
            client = await self.redis.redis_client
            await client.setex(token, expires, "blacklisted")
        except Exception as e:
            logger.error(f"Ошибка добавления токена в чёрный список: {e}")
            raise

    async def is_token_blacklisted(self, token: str) -> bool:
        """Проверка, находится ли токен в чёрном списке."""
        redis_client = await self.redis.redis_client
        return await redis_client.exists(token) == 1

    async def create_and_store_tokens(
        self, user_data: dict, response: Response
    ) -> dict:
        """Генерация и установка всех токенов."""
        access_token = self.create_access_token(user_data)
        refresh_token = self.create_refresh_token(user_data)
        csrf_token = self.create_csrf_token()
        self.set_token_cookie(response, access_token, refresh_token, csrf_token)
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "csrf_token": csrf_token,
        }
