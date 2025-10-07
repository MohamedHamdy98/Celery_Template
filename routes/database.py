from fastapi import APIRouter
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from schema.celery_task_executions import CeleryTaskExecution  # نفس الكلاس اللي عندك
import json

app = APIRouter(prefix="/api/v1", tags=["Database"])

# ✅ استخدم SQLite connection string للملف المحلي
DATABASE_URL = "sqlite+aiosqlite:///./database/celery_tasks.db"

engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


@app.get("/tasks")
async def get_all_tasks():
    """عرض كل التاسكات"""
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(CeleryTaskExecution))
        tasks = result.scalars().all()

        # نحولهم إلى dict قبل الإرسال
        def serialize(task):
            return {
                "execution_id": task.execution_id,
                "task_name": task.task_name,
                "task_args_hash": task.task_args_hash,
                "celery_task_id": task.celery_task_id,
                "status": task.status,
                "task_args": task.get_task_args() if task.task_args else None,
                "result": task.get_result() if task.result else None,
                "started_at": task.started_at,
                "completed_at": task.completed_at,
                "created_at": task.created_at,
                "updated_at": task.updated_at,
            }

        return {"tasks": [serialize(t) for t in tasks]}


@app.get("/tasks/{execution_id}")
async def get_task_by_id(execution_id: int):
    """عرض تاسك معينة برقمها"""
    async with AsyncSessionLocal() as session:
        result = await session.get(CeleryTaskExecution, execution_id)
        if not result:
            return {"error": "Task not found"}

        return {
            "execution_id": result.execution_id,
            "task_name": result.task_name,
            "status": result.status,
            "task_args": result.get_task_args(),
            "result": result.get_result(),
            "created_at": result.created_at,
            "updated_at": result.updated_at,
        }
