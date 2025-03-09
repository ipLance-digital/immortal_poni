from celery import Celery

from app.core.config import Settings

celery_app = Celery(
    "worker",
    broker=Settings().CELERY_BROKER_URL,
    backend=Settings().CELERY_RESULT_BACKEND,
)

celery_app.conf.update(
    result_expires=3600,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
