import logging
from typing import AsyncGenerator
from sqlalchemy.exc import SQLAlchemyError
from app.core.db.session import AsyncSessionLocal

logger = logging.getLogger(__name__)


async def get_db() -> AsyncGenerator:
    try:
        async with AsyncSessionLocal() as session:
            yield session
    except SQLAlchemyError as e:
        logger.exception(e)
