from celery import Celery
import sys, os
from helper.config import get_settings

settings = get_settings()

celery_app = Celery(
    "minirag",
    broker=settings.CELERY_BROKER_URL,         # e.g. amqp://user:pass@localhost:5672/vhost
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "tasks.file_processing",
        "tasks.data_indexing",
        "tasks.process_workflow",
        "tasks.maintenance",
        "tasks.mail_sender",
        "tasks.download_videos",
    ]
)

# Configure Celery with essential settings
celery_app.conf.update(
    # Serialization
    task_serializer=settings.CELERY_TASK_SERIALIZER,
    result_serializer=settings.CELERY_TASK_SERIALIZER,
    accept_content=[settings.CELERY_TASK_SERIALIZER],

    # Task safety
    task_acks_late=settings.CELERY_TASK_ACKS_LATE,

    # Time limits
    task_soft_time_limit=300,   # Graceful warning before kill
    task_time_limit=600,        # Hard kill if exceeds
    result_expires=3600,

    # Store results
    task_ignore_result=False,

    # Worker settings
    worker_concurrency=settings.CELERY_WORKER_CONCURRENCY,
    worker_prefetch_multiplier=2,

    # Connection reliability
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=10,
    broker_heartbeat=10,
    worker_cancel_long_running_tasks_on_connection_loss=True,

    # Task routing
    task_routes={
        "tasks.file_processing.process_project_files": {"queue": "file_processing"},
        "tasks.data_indexing.index_data_content": {"queue": "data_indexing"},
        "tasks.process_workflow.process_and_push_workflow": {"queue": "file_processing"},
        "tasks.maintenance.clean_celery_executions_table": {"queue": "default"},
        "tasks.mail_sender.send_email": {"queue": "mail_queue"},
        "tasks.download_videos.download_videos": {"queue": "urls_downloader_queue"},
    },

    # Periodic tasks
    beat_schedule={
        "cleanup-old-task-records": {
            "task": "tasks.maintenance.clean_celery_executions_table",
            "schedule": 10,   # run every 10s (change to crontab for prod)
            "args": (),
        }
    },

    # Transport options (RabbitMQ optimization)
    broker_transport_options={
        "visibility_timeout": 43200,  # 12 hours
        "fanout_prefix": True,
        "fanout_patterns": True,
    },

    # Timezone
    timezone="UTC",
)

# Default queue
celery_app.conf.task_default_queue = "default"
