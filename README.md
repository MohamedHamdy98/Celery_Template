# Project Setup and Run Instructions

## Run FastAPI Application
```bash
python -m uvicorn main:app --reload --host 0.0.0.0 --port 5000
```

## Run Docker Compose (RabbitMQ & Redis)
```bash
docker compose up --build rabbitmq redis
```

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

## To run the Beat scheduler, you can run the following command in a separate terminal:
```bash
python -m celery -A celery_app beat --loglevel=info
```

## Run Database 
```bash
python -m alembic revision --autogenerate -m "create celery_task_executions table"
python -m alembic upgrade head
```

