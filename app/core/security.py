from datetime import datetime, timedelta, UTC

import os
from jose import jwt
from passlib.context import CryptContext
from fastapi import Response

from app.core.redis import RedisSingleton


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(UTC) + timedelta(
        minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 300))
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode,
        os.getenv("SECRET_KEY"),
        algorithm=os.getenv("ALGORITHM"),
    )
    return encoded_jwt


def set_token_cookie(response: Response, token: str):
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 300)) * 60,
    )


async def blacklist_token(token: str, expires: int):
    try:
        client = await RedisSingleton().redis_client
        if client is None:
            raise Exception("Redis client is not initialized")
        await client.setex(token, expires, "blacklisted")
    except Exception as e:
        raise e


async def is_token_blacklisted(token: str) -> bool:
    redis_client = await RedisSingleton().redis_client
    return await redis_client.exists(token) == 1
