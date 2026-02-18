import sentry_sdk
from celery import Celery
from celery.schedules import crontab
from sentry_sdk.integrations.celery import CeleryIntegration

from core.config import settings

# Initialize Sentry for Celery workers
if settings.environment == "production" and settings.sentry_dsn_celery:
    sentry_sdk.init(
        dsn=settings.sentry_dsn_celery,
        environment=settings.environment,
        traces_sample_rate=settings.sentry_traces_sample_rate,
        profiles_sample_rate=settings.sentry_profiles_sample_rate,
        send_default_pii=False,
        integrations=[
            CeleryIntegration(
                monitor_beat_tasks=True,
                propagate_traces=True,
            ),
        ],
    )

celery_app = Celery(
    "arch-workers",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
    include=[
        "worker.my_task",
    ],
)

celery_app.conf.update(
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    broker_transport_options={
        "visibility_timeout": 43200,  # 12 hours
    },
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutes
    task_soft_time_limit=25 * 60,  # 25 minutes
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)

celery_app.conf.beat_schedule = {
    "example-task": {
        "task": "worker.my_task",
        "schedule": crontab(minute="*/5"),
    },
}
celery_app.autodiscover_tasks(["worker.my_task"])
