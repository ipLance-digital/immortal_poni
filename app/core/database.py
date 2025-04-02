import redis.asyncio as redis
import os
import logging

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession


class PgSingleton:
    """
    Пример использования атрибутов класса,
    если нужно соединение с базой или контекст.
    async def test():
        a = PgSingleton()
        async with a.session as session:
            async with session.begin():
    """

    _instance: "PgSingleton" = None
    _engine: AsyncEngine | None = None
    _session_maker: sessionmaker[AsyncSession] | None = None

    def __new__(cls, *args, **kwargs) -> "PgSingleton":
        if not cls._instance:
            cls._instance = super(PgSingleton, cls).__new__(cls)
        return cls._instance

    @property
    def engine(self) -> AsyncEngine:
        if not self._engine:
            self._engine = create_async_engine(os.getenv("DATABASE_URL"))
        return self._engine

    @property
    def session(self) -> AsyncSession:
        if not self._session_maker:
            self._session_maker = sessionmaker(
                bind=self.engine,
                class_=AsyncSession,
                expire_on_commit=False,
            )
        return self._session_maker()

    async def close_connections(self):
        """необязательная функция, но лучше перебдеть, чем недобдеть"""
        if self.engine:
            await self.engine.dispose()


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
                    ssl=os.getenv("REDIS_SSL", "false").lower() == "true",
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
