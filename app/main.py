"""
    Основной модуль приложения.
    Инициализирует FastAPI приложение, подключает роутеры и настраивает запуск сервера.
"""
from fastapi import FastAPI
import uvicorn
from app import database
from app.routers import get_router
from app.core.config import settings

database.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="""
    API для IP-lance. 
    """
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
        reload=settings.DEBUG
    )
