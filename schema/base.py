# from sqlalchemy.ext.declarative import declarative_base
# SQLAlchemyBase = declarative_base()

# schema/base.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base

SQLAlchemyBase = declarative_base()

DATABASE_URL = "sqlite+aiosqlite:///./database/celery_tasks.db"

engine = create_async_engine(
    DATABASE_URL, echo=False, future=True
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)
