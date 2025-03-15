from datetime import timedelta

from app.core.celery import celery_app

STALE_TASK_THRESHOLD = timedelta(minutes=10)

# Периодические задачи
celery_app.conf.beat_schedule = {
    "restart-stuck-tasks": {
        "task": "app.tasks.celery_period_tasks.restart_stuck_tasks",
        "schedule": timedelta(minutes=20),
    },
}
