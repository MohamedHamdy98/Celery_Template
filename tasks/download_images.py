
from celery_app_windows import celery_app
from schema.pydantic_schema import URLs
from typing import List
import aiohttp
import asyncio
import yt_dlp, os
from helper.idempotency_manager import IdempotencyManager
from schema.base import AsyncSessionLocal, engine


@celery_app.task(bind=True, name="tasks.download_images.download_images",
                 autoretry_for=(Exception,),
                 retry_kwargs={"max_retries": 3, "countdown": 60})
def download_images(self, urls: List[str]):
    """Celery entrypoint"""
    result = asyncio.run(_download_images(self, urls=urls))
    return result


async def _download_images(task_instance, urls: List[str]):
    """Async logic for downloading multiple images with idempotency tracking."""
    manager = IdempotencyManager(db_client=AsyncSessionLocal, db_engine=engine)

    task_name = "tasks.download_images.download_images"
    task_args = {"urls": urls}
    celery_task_id = task_instance.request.id

    # 🧠 Check if task already executed
    should_run, existing_task = await manager.should_execute_task(
        task_name=task_name,
        task_args=task_args,
        celery_task_id=celery_task_id,
        task_time_limit=1800,
    )

    if not should_run:
        print("⚠️ Skipping duplicate image download task.")
        if existing_task:
            return {
                "status": "SKIPPED",
                "previous_status": existing_task.status,
                "result": existing_task.get_result(),
                "execution_id": existing_task.execution_id
            }
        return {"status": "SKIPPED"}

    # 📝 Create a new task record
    record = await manager.create_task_record(
        task_name=task_name,
        task_args=task_args,
        celery_task_id=celery_task_id,
    )
    await manager.update_task_status(record.execution_id, "STARTED")

    try:
        # ================== Download Logic ==================
        output_path = os.path.join("Celery", "database", "downloaded_images")
        os.makedirs(output_path, exist_ok=True)

        if not urls:
            task_instance.update_state(
                state="FAILURE",
                meta={"signal": "No image URLs found!"}
            )
            raise Exception("No image URLs found!")

        results = []
        async with aiohttp.ClientSession() as session:
            for idx, url in enumerate(urls, start=1):
                task_instance.update_state(
                    state="PROGRESS",
                    meta={
                        "signal": f"Downloading image {idx}/{len(urls)}",
                        "current": idx,
                        "total": len(urls),
                    },
                )

                filename = os.path.basename(url.split("?")[0]) or f"image_{idx}.jpg"
                filepath = os.path.join(output_path, filename)

                try:
                    async with session.get(url) as response:
                        if response.status != 200:
                            raise Exception(f"Failed to download {url} (status: {response.status})")
                        with open(filepath, "wb") as f:
                            f.write(await response.read())

                    results.append({"url": url, "path": filepath})
                except Exception as e:
                    results.append({"url": url, "error": str(e)})

        final_result = {"status": "SUCCESS", "downloaded": results}

        await manager.update_task_status(record.execution_id, "SUCCESS", final_result)
        return final_result

    except Exception as e:
        await manager.update_task_status(
            record.execution_id,
            "FAILURE",
            {"error": str(e)}
        )
        print(f"❌ Error in _download_images: {e}")
        raise