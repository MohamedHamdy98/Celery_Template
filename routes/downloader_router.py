from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
import logging
import asyncio
from tasks.download_videos import download_videos
from celery_app_windows import celery_app
from celery.result import AsyncResult
from schema.pydantic_schema import URLs


logger = logging.getLogger("uvicorn.error")

downloader_router = APIRouter( prefix="/api/v1", tags=["Celery Template"])

@downloader_router.post("/download")
async def download_videos_from_urls(URLS: URLs):
    if URLS.urls:
        task_id = download_videos.delay(URLS.urls)
        return JSONResponse(
            content = {
                "signal": "Success!",
                "task_id": task_id.id
            }
        )
    else:
        return JSONResponse(
            content = {
                "signal": "Failure!",
                "task_id": task_id.id
            }
        )
    
@downloader_router.get("/task_status/{task_id}")
def get_status(task_id: str):
    result = AsyncResult(task_id, app=celery_app)
    return {
        "task_id": task_id,
        "status": result.status,
        "meta": result.info,
    }