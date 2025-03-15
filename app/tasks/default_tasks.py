from app.core.celery import celery_app

@celery_app.task
def celery_task():
    return "Test task"
