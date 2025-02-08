# immortal_poni

## Description

Фриланс платформа

## Technologies

- FastAPI
- SQLAlchemy
- PostgreSQL
- Docker
- Uvicorn
- Pytest

### Зависимости

Для установки зависимостей используйте команду:

- pip install uv
- uv venv --python=python3.12
- uv pip install -r requirements.txt

### Запуск

- uvicorn app.main:app --reload

или через python:

- python -m uvicorn app.main:app --reload

### API

Документация API доступна по адресу:

- host/docs

### Тесты

Для запуска тестов используйте команду:

- pytest

### Миграции

Для создания и применения миграций используйте команду:

- alembic init migrations
- alembic migrate

### Миграций

- Создать новую миграцию
alembic revision --autogenerate -m "описание изменений"

- Применить все миграции
alembic upgrade head

- Откатить на одну миграцию назад
alembic downgrade -1

- Посмотреть текущую версию БД
alembic current

- Посмотреть историю миграций
alembic history
