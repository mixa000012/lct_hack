from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from app.core import deps
from app.core.logs.logger import ContextLogger


class BaseView:
    db: AsyncSession = Depends(deps.get_db)
    request: Request
    logger = ContextLogger()
