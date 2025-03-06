from fastapi import FastAPI
import uvicorn
from app.core.config import Settings
from app.core.database import PgSingleton
from app.core.redis import RedisSingleton
from app.routers import get_router
from contextlib import asynccontextmanager
from sqlalchemy import text
import logging

logger = logging.getLogger("MAIN")
logging.basicConfig(level=logging.INFO)

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
        await RedisSingleton().init_redis()
        await RedisSingleton().redis_client.ping()
        logger.info("Redis подключён")
    except Exception as e:
        logger.error(f"Ошибка подключения к Redis: {e}")

    yield

    await db.close_connections()
    await RedisSingleton().close_redis()
    logger.info("Сервис был остановлен!")

app = FastAPI(
    title=Settings().APP_NAME,
    version="1.0.0",
    lifespan=lifespan,
)

router = get_router()
app.include_router(router, prefix=Settings().API_V1_STR)

@app.get("/")
def root():
    return {"message": "Welcome to IP-lance"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=Settings().LOCALHOST,
        port=Settings().PORT,
        reload=Settings().DEBUG,
    )
