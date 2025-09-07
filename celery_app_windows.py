# celery_app.py - Fixed for RabbitMQ on Windows
import os
import sys
from celery import Celery

# Ensure proper import path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import settings
from helper.config import get_settings
settings = get_settings()

# Create Celery app
celery_app = Celery('tasks')

# RabbitMQ + Windows specific configuration
celery_app.conf.update(
    # Your RabbitMQ connection
    broker_url=settings.CELERY_BROKER_URL,  # amqp://minirag_user:**@127.0.0.1:5672/minirag_vhost
    result_backend=settings.CELERY_RESULT_BACKEND,
    
    # CRITICAL: These settings fix the "not enough values to unpack" error on Windows
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    
    # Task discovery
    include=['tasks.mail_sender', "tasks.download_videos"],
    
    # IMPORTANT: Windows + RabbitMQ specific worker settings
    worker_pool='solo',  # Must use solo pool on Windows with RabbitMQ
    worker_concurrency=2,
    worker_prefetch_multiplier=2,
    
    # Task settings
    task_ignore_result=False,
    result_expires=3600,
    task_acks_late=False,
    
    # RabbitMQ connection settings
    broker_connection_retry_on_startup=True,
    broker_connection_retry=True,
    broker_connection_max_retries=10,
    broker_heartbeat=10,  # Add heartbeat for RabbitMQ
    
    # Task routing
    task_routes={
        'tasks.mail_sender.send_email': {'queue': 'mail_queue'},
        "tasks.download_videos.download_videos": {'queue': 'urls_downloader_queue'}
    },
    task_default_queue='default',
    
    # Windows-specific settings to prevent the unpacking error
    worker_disable_rate_limits=True,
    task_always_eager=False,  # Make sure this is False
    task_eager_propagates=False,
    
    # Time limits
    task_soft_time_limit=300,
    task_time_limit=600,
    
    # CRITICAL: This setting often fixes the unpacking error
    worker_send_task_events=False,
    task_send_sent_event=False,
    
    # RabbitMQ specific optimizations
    broker_transport_options={
        'visibility_timeout': 43200,  # 12 hours
        'fanout_prefix': True,
        'fanout_patterns': True
    }
)

# Set timezone
celery_app.conf.timezone = 'UTC'

if __name__ == '__main__':
    celery_app.worker_main([
        'worker',
        '--loglevel=info',
        '--pool=solo',  # Force solo pool
        '--concurrency=1',
        '--without-gossip',  # Disable gossip
        '--without-mingle',  # Disable mingle
        '--without-heartbeat'  # Disable heartbeat
    ])