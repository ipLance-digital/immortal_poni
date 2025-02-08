"""
Модуль для работы с базой данных.
Содержит настройки подключения и сессии SQLAlchemy.
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    pool_size=settings.DB_POOL_SIZE,
    max_overflow=settings.DB_MAX_OVERFLOW
)

# Фабрика сессий
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Базовый класс для моделей
Base = declarative_base()

def get_db():
    """
    Генератор для получения сессии базы данных.
    Автоматически закрывает сессию после использования.
    
    Yields:
        Session: Сессия SQLAlchemy
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
