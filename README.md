# ipLance(immortal_poni)
### Фриланс платформа

## Стэк

- FastAPI
- SQLAlchemy
- PostgreSQL
- Docker
- Uvicorn
- Pytest

### Зависимости

Для установки зависимостей используйте команду:

#### python -m venv .venv

#### unix:source .venv/bin/activate

#### win: ./.venv/Scripts/activate

#### pip install uv 

#### uv pip install -r requirements.txt

### Запуск

#### uvicorn app.main:app --reload

или через python:

#### python -m uvicorn app.main:app --reload

### API

Документация API доступна по адресу:

- host/docs

### Тесты

Для запуска тестов используйте команду:

(!при проведении тестов апи нужно поднять локальный сервер, для корректного обращения к редису)

#### pytest


### Миграции
Команды по миграциям лежат в alembic/README
Создать новую миграцию

#### win - python .\app\scripts\safe_migrate.py
#### *nix - python app/scripts/safe_migrate.py

### База данных

Асинхронное подключение к базе данных.
Модуль инициализации базы данных:
app.core.database.py

#### Хранилище

Организовано облачное хранилище на базе supabase.com вместе с бд.
Работает через моудль supabase.

https://supabase.com/dashboard/project/fbvupbfiavdrewoxrtwp

Для получения доступа писать brevnishko2 или SerMichbboy


### Redis

редис подключен в redis-cloud.
Для мониторинга redis есть ПО:

#### sudo apt update

#### sudo apt install snapd

#### sudo snap install redisinsight

### flower

Мониторинг задач селери  > host:5555

### Celery



---
