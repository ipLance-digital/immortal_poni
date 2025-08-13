# ✨ ipLance ✨ (immortal_poni) 🐎💨
---
### ip-lance.com
<br>  
<br>  

&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;![Immortal pony](https://media.tenor.com/tzGECrYAY20AAAAj/mlp-wave-mlp-pony-wave.gif)


## 🐍 Стэк
- FastAPI
- SQLAlchemy
- PostgreSQL
- Docker
- Uvicorn
- Pytest

---

## ❕ Зависимости
Для установки зависимостей используйте команды:
#### python3.12 -m venv .venv
#### source .venv/bin/activate
#### pip install uv
#### uv pip install -r requirements.txt

---

## ❗ Run
### Docker
#### docker compose up --build
### Запуск локально
#### uvicorn app.main:app --reload
или через python:
#### python -m uvicorn app.main:app --reload

---

# 💥 API
Документация API доступна по адресу:
- host/docs

---

## 💩 Тесты
Для запуска тестов используйте команду:
#### pytest
(!при проведении тестов апи нужно поднять локальный сервер, для корректного обращения к редису)

---

## 💤 Миграции
Команды по миграциям лежат в alembic/README

Создать новую миграцию
#### win - python .\app\scripts\safe_migrate.py
#### *nix - python app/scripts/safe_migrate.py

---

## 🌟 Supabase
#### База данных
Асинхронное подключение к базе данных.
Модуль инициализации базы данных:

app.core.database.py

#### Хранилище
Организовано облачное хранилище на базе supabase.com вместе с бд.
Работает через моудль supabase.

https://supabase.com/dashboard/project/fbvupbfiavdrewoxrtwp

Для получения доступа писать brevnishko2 или SerMichbboy

---

## 👽 Redis
редис подключен в redis-cloud.
Для мониторинга redis есть ПО:

#### sudo apt update
#### sudo apt install snapd
#### sudo snap install redisinsight

---

## 🌵 Flower

Мониторинг задач селери  > host:5555

---

## 💌 Celery
В модуле app/tasks/config_tasks выставляются настройки выполнения задач.

- celery_app.conf.beat_schedule - выполнение периодических задач
---
## 🌜 Авторизация
Авторизация в данном приложении реализована с 
использованием токенов JWT (JSON Web Tokens) для 
обеспечения безопасного доступа пользователей к защищённым маршрутам. 
Система включает следующие ключевые аспекты:

#### Регистрация и вход: 

Пользователь регистрируется или входит через предоставление 
имени пользователя, email или телефона и пароля. Пароль хешируется с 
использованием bcrypt через passlib для защиты данных. Вход возможен 
по одному из трёх идентификаторов (username, email, phone), что добавляет
гибкость.

#### Токены:

- Access Token: Краткосрочный токен (по умолчанию 300 минут), 
используемый для аутентификации запросов. Содержит информацию о пользователе
(sub) и срок действия (exp).
- Refresh Token: Долгосрочный токен (по умолчанию 30 дней), позволяет обновить 
access token без повторного ввода учетных данных.
- CSRF Token: Генерируется случайным образом и используется для защиты от 
атак CSRF. Используется на фронте с передачей в хэдерсы и в
- дальнейшем сравнивая токены X-CSRF-TOKEN с CSRF токеном в куках на стороне сервера.

#### Безопасность:

Токены передаются через защищённые HTTP-only cookies с атрибутами secure
и samesite="lax", что предотвращает их перехват через XSS и ограничивает 
использование в межсайтовых запросах.
Токены могут быть добавлены в чёрный список в Redis (например, при выходе),
что позволяет аннулировать их до истечения срока действия.
Проверка подлинности осуществляется декодированием JWT с использованием 
секретного ключа (SECRET_KEY) и алгоритма (ALGORITHM).
Обновление токенов: Эндпоинт /refresh позволяет обновить access token с 
использованием refresh token, сохраняя безопасность через проверку CSRF и 
чёрного списка.
Выход: При выходе токен добавляется в чёрный список, и все cookies удаляются, 
завершая сессию.
Эта система обеспечивает многоуровневую защиту, включая шифрование, проверку 
токенов и защиту от CSRF-атак.

---
