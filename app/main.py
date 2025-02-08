"""
Основной модуль приложения.
Инициализирует FastAPI приложение, подключает роутеры и настраивает запуск сервера.
"""
from fastapi import FastAPI
import uvicorn
from app.database import engine, Base
from app.routers import get_router
from app.core.config import settings


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="""
    API для фриланс платформы. 
    
    ## Возможности
    * Регистрация и авторизация пользователей
    * Управление профилями
    * JWT авторизация
    """
)

router = get_router()
app.include_router(router, prefix=settings.API_V1_STR)

@app.get("/")
def root():
    """
    Корневой эндпоинт для проверки работоспособности API.
    
    Returns:
        dict: Приветственное сообщение
    """
    return {"message": "Welcome to IP-lance"}

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.LOCALHOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )


