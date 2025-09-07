# tasks/mail_sender.py - Simplified version to debug the issue
import time
import logging
from datetime import datetime
from celery import current_task
from schema.pydantic_schema import URLs

# Import after Celery app is created to avoid circular imports
from celery_app_windows import celery_app

logger = logging.getLogger("mail_tasks")

@celery_app.task(bind=True, name='tasks.mail_sender.send_email')
def send_email(self, time_wait: int):
    """
    Simple email task without complex async operations.
    This should avoid the unpacking error.
    """
    try:
        task_id = self.request.id
        logger.info(f"Starting email task {task_id} with wait time: {time_wait}")
        
        started_at = datetime.now()
        
        # Update initial state
        self.update_state(
            state='PROGRESS',
            meta={
                'current': 0,
                'total': 5,
                'started_at': started_at.isoformat(),
                'status': 'Starting email process...'
            }
        )
        
        # Send emails with progress updates
        for i in range(5):
            time.sleep(time_wait)
            
            current_progress = i + 1
            self.update_state(
                state='PROGRESS',
                meta={
                    'current': current_progress,
                    'total': 5,
                    'started_at': started_at.isoformat(),
                    'status': f'Sent email {current_progress}/5'
                }
            )
            
            logger.info(f"Email {current_progress} sent (task: {task_id})")
        
        finished_at = datetime.now()
        duration = finished_at - started_at
        
        result = {
            'task_id': task_id,
            'started_at': started_at.isoformat(),
            'finished_at': finished_at.isoformat(),
            'duration_seconds': duration.total_seconds(),
            'emails_sent': 5,
            'status': 'completed'
        }
        
        logger.info(f"Task {task_id} completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Task failed: {str(e)}", exc_info=True)
        # Don't update state here, let Celery handle the failure
        raise


# Simple test task to verify Celery is working
@celery_app.task(name='tasks.mail_sender.test_task')
def test_task(message: str = "Hello from Celery!"):
    """Simple test task to verify Celery setup"""
    logger.info(f"Test task executed: {message}")
    return {
        'message': message,
        'timestamp': datetime.now().isoformat(),
        'status': 'success'
    }

# Debug task to check Celery internals
@celery_app.task(bind=True, name='tasks.mail_sender.debug_task')
def debug_task(self):
    """Debug task to inspect Celery state"""
    return {
        'task_id': self.request.id,
        'task_name': self.name,
        'args': self.request.args,
        'kwargs': self.request.kwargs,
        'retries': self.request.retries,
        'eta': str(self.request.eta),
        'expires': str(self.request.expires),
    }