# immortal_poni

## Описание

Фриланс платформа

## Технологии

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

- export PYTHONPATH=$(pwd)
- pytest

### Миграции

- Создать новую миграцию

python .\app\scripts\safe_migrate.py

### Базы данных

Асинхронное подключение к базе данных.
Модуль инициализации базы данных:
app.database.py

### Redis

Для мониторинга redis есть ПО:

sudo apt update
sudo apt install snapd
sudo snap install redisinsight
