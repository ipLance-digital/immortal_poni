from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import redis.asyncio as redis
import os
import asyncio


class RedisSingleton:
    _instance = None
    _redis_client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RedisSingleton, cls).__new__(cls)
        return cls._instance

    async def init_redis(self):
        if self._redis_client is None:
            self._redis_client = await redis.Redis(
                host=os.getenv("REDIS_HOST"),
                port=int(os.getenv("REDIS_PORT")),
                password=os.getenv("REDIS_PASSWORD"),
                username=os.getenv("REDIS_USERNAME") ,
                db=int(os.getenv("REDIS_DB")),
            )

    @property
    def redis_client(self) -> redis.Redis:
        if self._redis_client is None:
            raise ValueError("Redis не инициализирован")
        return self._redis_client

    async def close_connections(self):
        if self._redis_client:
            await self._redis_client.close()
            self._redis_client = None

redis_instance = RedisSingleton()

async def get_redis():
    await redis_instance.init_redis()
    return redis_instance.redis_client


async def test_redis():
    try:
        redis = await get_redis()
        print("Redis Cloud подключён:", await redis.ping())
    except Exception as e:
        print(f"Ошибка подключения к Redis Cloud: {e}")

if __name__ == "__main__":
    asyncio.run(test_redis())
    