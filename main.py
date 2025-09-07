# fastApi
from fastapi import FastAPI
from helper.config import get_settings
from routes.basic_router import basic_router
from routes.downloader_router import downloader_router

app = FastAPI()

settings = get_settings()

app.include_router(basic_router)
app.include_router(downloader_router)


@app.get("/health")
def get_health():
    return {"status": "Azkaban"}

# uvicorn main:app --reload --host 0.0.0.0 --port 5000