from fastapi import FastAPI
import uvicorn
from fastapi.responses import HTMLResponse
from app.core.database import PgSingleton, RedisSingleton
from app.routers import get_router
from contextlib import asynccontextmanager
from sqlalchemy import text
import logging
from dotenv import load_dotenv
import os
from starlette.middleware.cors import CORSMiddleware
from app.utils.websocket.chat.websocket_router import router as websocket_router

logger = logging.getLogger("  app  ")
logging.basicConfig(level=logging.INFO)

load_dotenv()


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
        logger.info("Redis подключён")
    except Exception as e:
        logger.error(f"Ошибка подключения к Redis: {e}")

    yield

    await db.close_connections()
    await RedisSingleton().close_redis()
    logger.info("Сервис был остановлен!")


app = FastAPI(
    title="IP-lance API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,  # type: ignore
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = get_router()
app.include_router(router, prefix="/api/v1")
# требуется для работоспособности websocket
app.include_router(websocket_router)


@app.get("/")
def root():
    with open("app/services/static/main_page.html", "r") as file:
        content = file.read()
    return HTMLResponse(content=content)


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "True").lower() == "true",
    )
