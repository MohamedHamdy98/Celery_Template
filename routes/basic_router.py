from fastapi import APIRouter, Depends, HTTPException
from helper.config import get_settings, Settings
import logging
import asyncio
from tasks.mail_sender import send_email
from celery_app_windows import celery_app
from celery.result import AsyncResult

logger = logging.getLogger("uvicorn.error")

basic_router = APIRouter( prefix="/api/v1", tags=["api_v1"] )

@basic_router.get("/send_mails")
async def send_mails(
    time_wait: int = 3,
    settings: Settings = Depends(get_settings)
):
    """
    Trigger email sending task
    """
    try:
        logger.info(f"Starting email sending task with wait time: {time_wait} seconds")
        
        # Start the Celery task
        task = send_email.delay(time_wait)
        
        logger.info(f"Email task started with ID: {task.id}")
        
        return {
            "message": "Email sending task started",
            "task_id": task.id,
            "status": "PENDING",
            "check_status_url": f"/api/v1/task_status/{task.id}"
        }
        
    except Exception as e:
        logger.error(f"Error starting email task: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to start email task: {str(e)}"
        )
    
@basic_router.get("/task_status/{task_id}")
async def get_task_status(task_id: str):
    """
    Check the status of a Celery task
    """
    try:
        # Get task result
        task_result = AsyncResult(task_id, app=celery_app)
        
        if task_result.state == "PENDING":
            response = {
                "task_id": task_id,
                "state": task_result.state,
                "status": "Task is waiting to be processed"
            }
        elif task_result.state == "PROGRESS":
            response = {
                "task_id": task_id,
                "state": task_result.state,
                "current": task_result.info.get("current", 0),
                "total": task_result.info.get("total", 1),
                "status": task_result.info.get("status", ""),
                "started_at": task_result.info.get("started_at", "")
            }
        elif task_result.state == "SUCCESS":
            response = {
                "task_id": task_id,
                "state": task_result.state,
                "result": task_result.result
            }
        elif task_result.state == "FAILURE":
            response = {
                "task_id": task_id,
                "state": task_result.state,
                "error": str(task_result.info),
                "traceback": task_result.traceback
            }
        else:
            response = {
                "task_id": task_id,
                "state": task_result.state,
                "info": task_result.info
            }
            
        return response
        
    except Exception as e:
        logger.error(f"Error checking task status: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to check task status: {str(e)}"
        )

@basic_router.delete("/cancel_task/{task_id}")
async def cancel_task(task_id: str):
    """
    Cancel a running Celery task
    """
    try:
        celery_app.control.revoke(task_id, terminate=True)
        return {
            "message": f"Task {task_id} has been cancelled",
            "task_id": task_id
        }
    except Exception as e:
        logger.error(f"Error cancelling task: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel task: {str(e)}"
        )