import redis.asyncio as redis
import os


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
                username=os.getenv("REDIS_USERNAME"),
                db=int(os.getenv("REDIS_DB")),
            )

    @property
    def redis_client(self) -> redis.Redis:
        if self._redis_client is None:
            raise ValueError("Redis не инициализирован")
        return self._redis_client
