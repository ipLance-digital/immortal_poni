from app.core.celery import celery_app

@celery_app.task
def test_task():
    return "Test task"
