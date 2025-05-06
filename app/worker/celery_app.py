from datetime import timedelta

from celery import Celery
from celery.schedules import crontab

from app.core.config import settings

from app.worker.tasks import task_check_confirmations, task_fail_stale

celery_app = Celery(
    "worker",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.beat_schedule = {
    "check-confirmations-every-minute": {
        "task": task_check_confirmations.name,
        "schedule": timedelta(minutes=1),
    },
    "fail-stale-wallets-daily": {
        "task": task_fail_stale.name,
        "schedule": crontab(hour=0, minute=0),
    },
}

celery_app.autodiscover_tasks(["app.worker"])

