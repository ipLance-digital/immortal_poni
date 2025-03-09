from app.core.celery import celery_app

@celery_app.task
def add(x, y):
    return x + y

@celery_app.task
def send_email(to, subject):
    print(f"Sending email to {to} with subject {subject}")
    return True
