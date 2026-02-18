from contextlib import contextmanager
from typing import Generator

from core.config import settings
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker

async_engine = create_async_engine(settings.database_url_asyncpg, echo=True, pool_pre_ping=True, future=True)
async_session = async_sessionmaker(
    bind=async_engine,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

sync_engine = create_engine(settings.database_url_psycopg, pool_pre_ping=True)
SessionLocal = sessionmaker(
    bind=sync_engine,
    autocommit=False,
    autoflush=False,
)


# for async api
async def get_pg_db():
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


#for sync api
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# for celery worker
@contextmanager
def get_db_context() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
