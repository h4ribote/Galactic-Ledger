import os
from celery import Celery
from celery.schedules import crontab

# Get Redis URL from env or use default
CELERY_BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
CELERY_RESULT_BACKEND = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/0")

celery_app = Celery(
    "galactic_ledger",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

celery_app.conf.imports = [
    "app.tasks"
]

# Beat Schedule
celery_app.conf.beat_schedule = {
    "update-construction-every-minute": {
        "task": "app.tasks.update_construction_status_task",
        "schedule": crontab(minute="*"), # Every minute
    },
    "produce-resources-every-minute": {
        "task": "app.tasks.produce_resources_task",
        "schedule": crontab(minute="*"), # Every minute
    },
}
