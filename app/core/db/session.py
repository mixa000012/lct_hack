from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import settings

engine = create_async_engine(
    settings.PG_DATABASE_URI,
    pool_size=settings.PG_POOL_MAX_SIZE,
    pool_recycle=settings.PG_POOL_RECYCLE,
    max_overflow=settings.PG_MAX_OVERFLOW,
    pool_pre_ping=True,
)
AsyncSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)
