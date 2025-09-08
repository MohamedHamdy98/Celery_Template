# Project Setup and Run Instructions

## Run Celery Worker
```bash
python -m celery -A celery_app_windows worker -Q default,urls_downloader_queue,mail_queue --loglevel=info
```

## Run Celery Worker by flower
```bash
python -m celery -A celery_app_windows flower --port=5555
```
## Run Celery Worker by flower + config file
```bash
python -m celery -A celery_app_windows flower --conf=flowerconfig.py
```


## Run FastAPI Application
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

## Run Docker Compose (RabbitMQ & Redis)
```bash
docker compose up --build rabbitmq redis
```
