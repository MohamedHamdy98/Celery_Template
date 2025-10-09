from celery_app_windows import celery_app
from helper.config import get_settings
import asyncio
from schema.base import AsyncSessionLocal, engine
from helper.idempotency_manager import IdempotencyManager

import logging
logger = logging.getLogger(__name__)

@celery_app.task(
                 bind=True, name="tasks.maintenance.clean_celery_executions_table",
                 autoretry_for=(Exception,),
                 retry_kwargs={'max_retries': 3, 'countdown': 60}
                )
def clean_celery_executions_table(self):

    return asyncio.run(
        _clean_celery_executions_table(self)
    )

async def _clean_celery_executions_table(task_instance):

    db_engine, vectordb_client = None, None
    
    try:
        db_engine = engine
        # Create idempotency manager
        idempotency_manager = IdempotencyManager(db_client=AsyncSessionLocal, db_engine=engine)

        logger.warning(f"cleaning !!!")
        _ = await idempotency_manager.cleanup_old_tasks(5)

        return True

    except Exception as e:
        logger.error(f"Task failed: {str(e)}")
        raise
    finally:
        try:
            if db_engine:
                await db_engine.dispose()
            
            if vectordb_client:
                await vectordb_client.disconnect()
        except Exception as e:
            logger.error(f"Task failed while cleaning: {str(e)}")