from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings


class Base(DeclarativeBase):
    pass


# СИНХРОННЫЙ ПУЛ
engine = create_engine(url=settings.DATABASE_URL_psycopg, echo=True)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)

#  АСИНХРОННЫЙ ПУЛ
async_engine = create_async_engine(url=settings.DATABASE_URL_psycopg_async, echo=True)
async_session_factory = async_sessionmaker(bind=async_engine, expire_on_commit=False, autoflush=False)
