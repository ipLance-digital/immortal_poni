FROM python:3.12-alpine

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Устанавливаем пакеты для сборки Python-библиотек (gcc, musl-dev и др.)
RUN apk add --no-cache gcc musl-dev linux-headers libffi-dev openssl-dev

# Копируем файл с зависимостями и устанавливаем их
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# Копируем весь проект в контейнер
COPY ./app ./app

# Открываем порт, на котором будет работать приложение
EXPOSE 8000

# Команда для запуска приложения (в режиме разработки с авто-перезагрузкой)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

