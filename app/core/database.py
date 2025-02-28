from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import Settings


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
            self._engine = create_async_engine(Settings().DATABASE_URL)
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
