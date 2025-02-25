"""
Основной модуль приложения.
Инициализирует FastAPI приложение, подключает роутеры и настраивает запуск сервера.
"""

from fastapi import FastAPI
import uvicorn
from app.database import PgSingleton
from app.redis import get_redis
from app.routers import get_router
from app.core.config import settings
from contextlib import asynccontextmanager
from sqlalchemy import text
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Приложение запускается...")
    db = PgSingleton()
    
    try:
        async with db.session as session:
            await session.execute(text("SELECT 1"))
        logger.info("Подключение к базе без ошибок")
    except Exception as e:
        logger.error(f"Ошибка подключения к БД: {e}")

    try:
        redis = await get_redis()
        await redis.ping()
        logger.info("Redis подключён")
    except Exception as e:
        logger.error(f"Ошибка подключения к Redis: {e}")

    yield

    await db.close_connections() 
    redis = await get_redis()  
    await redis.close()
    logger.info("Моя остановочкаааа")

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="""
    API для IP-lance. 
    """,
    lifespan=lifespan,
)

router = get_router()
app.include_router(router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    """
    Корневой эндпоинт для проверки API.

    Returns:
        dict: message
    """
    return {"message": "Welcome to IP-lance"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.LOCALHOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )