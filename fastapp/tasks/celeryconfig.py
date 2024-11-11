from celery import Celery
from celery.schedules import crontab

import config


CELERY_BROKER_URL = config.CELERY_BROKER_URL
CELERY_BACKEND_URL = config.CELERY_BACKEND_URL

celery_app = Celery(__name__, broker=CELERY_BROKER_URL, backend=CELERY_BACKEND_URL)

celery_app.conf.update(
    imports=['fastapp.tasks.celery_tasks'],
    broker_connection_retry_on_startup=True,
    task_track_started=True
)

celery_app.conf.beat_schedule = {
    'delete_expired_codes_every_minute': {
        'task': 'fastapp.tasks.celery_tasks.delete_expired_codes',
        'schedule': crontab(),  # Every minute
    },
}