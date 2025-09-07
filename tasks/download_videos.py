from celery_app_windows import celery_app
from schema.pydantic_schema import URLs
from typing import List
import asyncio
import yt_dlp, os

'''
- You will have 2 functions, the first one is for celery_app and the second for the logic.
- def download_video(url: str, output_path: str):
    """
    Download video from YouTube, TikTok, Twitter, etc. using yt-dlp.
    """
    ydl_opts = {
        "outtmpl": output_path,  # Save to given filename
        "format": "bestvideo+bestaudio/best"
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    print(f"✅ Video downloaded to {output_path}")
'''
@celery_app.task(bind=True, name="tasks.download_videos.download_videos")
def download_videos(self, urls: List[str]):
    result = asyncio.run(_download_videos(self, urls=urls))
    return result



async def _download_videos(task_instance, urls: List[str]):
    try:
        output_path = os.path.join("Celery", "database", "downloads_videos")
        os.makedirs(output_path, exist_ok=True)

        ydl_opts = {
            "outtmpl": os.path.join(output_path, "%(title)s.%(ext)s"),
            "format": "bestvideo+bestaudio/best"
        }

        if not urls:
            task_instance.update_state(
                state="FAILURE",
                meta={"signal": "No URLs have been found!"}
            )
            raise Exception("No URLs have been found!")

        results = []
        for idx, url in enumerate(urls, start=1):
            task_instance.update_state(
                state="PROGRESS",
                meta={"signal": f"Downloading {idx}/{len(urls)}", "current": idx, "total": len(urls)},
            )
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            results.append({"url": url, "path": output_path})

        return {"status": "SUCCESS", "downloaded": results}

    except Exception as e:
        print(f"❌ Error in _download_videos: {e}")
        raise
