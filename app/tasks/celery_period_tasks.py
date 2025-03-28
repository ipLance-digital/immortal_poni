from datetime import datetime
from app.core.celery import celery_app
from app.main import logger
from app.tasks.config import STALE_TASK_THRESHOLD
from celery.exceptions import SoftTimeLimitExceeded


@celery_app.task(bind=True, max_retries=3)
def restart_stuck_tasks(self):
    """
    Периодическая задача,
    которая проверяет статусы задач, и закрывает зависшие.
    При этом задача будет перезапущена не более 3 раз.
    """
    inspect = celery_app.control.inspect()
    active_tasks = inspect.active() or {}
    now = datetime.utcnow()

    for worker, tasks in active_tasks.items():
        for task in tasks:
            task_id = task["id"]
            task_name = task["name"]
            received_time = datetime.utcfromtimestamp(task["time_start"])
            if now - received_time > STALE_TASK_THRESHOLD:
                current_retries = task.get("retries", 0)
                if current_retries < 3:
                    try:
                        celery_app.control.revoke(task_id, terminate=True)
                        celery_app.send_task(
                            task_name,
                            args=task.get("args", []),
                            kwargs=task.get("kwargs", {}),
                            retries=current_retries + 1,
                        )
                        logger.info(
                            f"restart_stuck_tasks: "
                            f"Revoked and rescheduled task "
                            f"{task_id} ({task_name}), "
                            f"attempt {current_retries + 1}"
                        )
                    except SoftTimeLimitExceeded:
                        logger.error(f"Task {task_id} exceeded time limit and failed.")
                        self.retry(countdown=60)
                else:
                    logger.error(f"Task {task_id} failed after 3 attempts.")

    return "Revision finished"
