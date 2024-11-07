from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase
from sqlalchemy import URL, create_engine, text
from config import settings

"""створення синхронний движок для підключення до бази даних"""
sync_engine = create_engine(
    url=settings.database_url_psycopg,
    echo=True,
    pool_size=5,
    max_overflow=10
)

"""створення асинхронний движок для підключення до бази даних"""
async_engine = create_async_engine(
    url=settings.database_url_asyncpg,
    echo=True,
    pool_size=5,
    max_overflow=10
)

"""Створення сесії синхронної та асинхронної"""
session_factory = sessionmaker(sync_engine)
async_session_factory = async_sessionmaker(async_engine)



