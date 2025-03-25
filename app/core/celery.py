from celery import Celery
from dotenv import load_dotenv
import os

load_dotenv()

celery_app = Celery(
    "alpha_worker",
    broker=os.getenv("CELERY_BROKER_URL"),
    backend=os.getenv("CELERY_RESULT_BACKEND"),
)

celery_app.conf.update(
    result_expires=3600,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    broker_pool_limit=10,
    broker_connection_retry_on_startup=True,
)

# импорт селери модулей
celery_app.conf.imports = (
    "app.tasks.default_tasks",
    "app.tasks.celery_period_tasks",
    "app.tasks.email_tasks",
)

# хранение celerybeat-schedule
celery_app.conf.beat_schedule_filename = os.path.join(
    os.path.dirname(os.path.dirname(__file__)),
    'tasks', 'celerybeat-schedule'
)
