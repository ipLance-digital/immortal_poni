FROM python:3.12-alpine

WORKDIR /app

RUN apk add --no-cache gcc musl-dev linux-headers libffi-dev openssl-dev

RUN pip install --no-cache-dir uv

COPY requirements.txt .

RUN uv pip install -r requirements.txt --system

COPY ./app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
