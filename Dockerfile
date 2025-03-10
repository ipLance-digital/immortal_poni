FROM python:3.12-alpine

WORKDIR /app

RUN apk add --no-cache gcc musl-dev linux-headers libffi-dev openssl-dev

COPY requirements.txt .

RUN pip install --upgrade pip && pip install -r requirements.txt

COPY ./app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

