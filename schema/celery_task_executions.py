from .base import SQLAlchemyBase
from sqlalchemy import Column, Integer, DateTime, func, String, Text, Index
import json

class CeleryTaskExecution(SQLAlchemyBase):
    __tablename__ = "celery_task_executions"

    execution_id = Column(Integer, primary_key=True, autoincrement=True)

    task_name = Column(String(255), nullable=False)
    task_args_hash = Column(String(64), nullable=False)  # SHA-256 hash of task arguments
    celery_task_id = Column(String(36), nullable=True)  # UUID string بدل UUID field

    status = Column(String(20), nullable=False, default="PENDING")

    task_args = Column(Text, nullable=True)   # JSON dump
    result = Column(Text, nullable=True)      # JSON dump

    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)

    __table_args__ = (
        Index("ixz_task_name_args_celery_hash", "task_name", "task_args_hash", "celery_task_id", unique=True),
        Index("ixz_task_execution_status", "status"),
        Index("ixz_task_execution_created_at", "created_at"),
        Index("ixz_celery_task_id", "celery_task_id"),
    )

    # Helpers للتعامل مع JSON
    def set_task_args(self, value: dict):
        self.task_args = json.dumps(value) if value is not None else None

    def get_task_args(self):
        return json.loads(self.task_args) if self.task_args else None

    def set_result(self, value: dict):
        self.result = json.dumps(value) if value is not None else None

    def get_result(self):
        return json.loads(self.result) if self.result else None
