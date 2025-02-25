from datetime import datetime, timedelta
from jose import jwt
from passlib.context import CryptContext
import os
from app.redis import get_redis

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 300))
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, os.getenv("SECRET_KEY"), algorithm=os.getenv("ALGORITHM")
    )
    return encoded_jwt

async def blacklist_token(token: str, expires: int):
    try:
        client = await get_redis() 
        if client is None:
            raise Exception("Redis client is not initialized")
        await client.setex(token, expires, "blacklisted") 
    except Exception as e:
        raise


async def is_token_blacklisted(token: str) -> bool:
    """
    Проверяет, находится ли токен в черном списке в Redis.
    """
    redis_client = await get_redis()  
    return await redis_client.exists(token) == 1  

