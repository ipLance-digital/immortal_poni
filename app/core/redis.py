import redis.asyncio as redis
import os
import logging


class RedisSingleton:
    _instance = None
    _redis_client = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def init_redis(self):
        if self._redis_client is None:
            try:
                self._redis_client = await redis.Redis(
                    host=os.getenv("REDIS_HOST", "localhost"),
                    port=int(os.getenv("REDIS_PORT", 6379)),
                    password=os.getenv("REDIS_PASSWORD", ""),
                    username=os.getenv("REDIS_USERNAME", ""),
                    db=int(os.getenv("REDIS_DB", 0)),
                    ssl=os.getenv("REDIS_SSL", "false").lower() == "true"
                )
            except Exception as e:
                raise ConnectionError("Не удалось подключиться к Redis")

    async def close_redis(self):
        if self._redis_client:
            try:
                await self._redis_client.aclose()
                self._redis_client = None
                logging.info("Redis соединение закрыто.")
            except Exception as e:
                logging.error(f"Ошибка при закрытии соединения с Redis: {e}")

    @property
    async def redis_client(self) -> redis.Redis:
        if self._redis_client is None:
            await self.init_redis()
        return self._redis_client
