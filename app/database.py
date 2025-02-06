from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from urllib.parse import quote_plus

load_dotenv()

password = os.getenv("DB_PASSWORD", "050592")
encoded_password = quote_plus(password)
DATABASE_URL = f"postgresql://postgres:{encoded_password}@localhost:5432/main_it_lance_db"

try:
    engine = create_engine(DATABASE_URL)
    engine.connect()
except Exception as e:
    print(f"Ошибка подключения к базе данных: {e}")
    raise

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
