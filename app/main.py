import asyncio
import logging
import uvicorn
from fastapi import FastAPI
from starlette.middleware import Middleware
from starlette_context.middleware import RawContextMiddleware
from tenacity import after_log, before_log, retry, stop_after_attempt, wait_fixed
from sqlalchemy import text
from app.api.v1.api import api_router
from app.core.config import settings
from app.core.db.session import AsyncSessionLocal
from app.core.logs.log import setup_logging
from app.core.middlewares import (
    ContextMiddleware,
    ExceptionMiddleware,
    LogMiddleware,
)


middleware = [
    Middleware(RawContextMiddleware),
    Middleware(ContextMiddleware),
    Middleware(LogMiddleware),
    Middleware(ExceptionMiddleware),
]
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    debug=settings.DEBUG,
    middleware=middleware,
)
app.include_router(api_router, prefix=settings.API_V1_STR)

app_monit = FastAPI()


logger = logging.getLogger()


@app.on_event("startup")
def set_logging() -> None:
    setup_logging()


@app.on_event("startup")
@retry(
    stop=stop_after_attempt(60 * 5),
    wait=wait_fixed(1),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
async def init() -> None:
    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))  # type: ignore
            logger.info("Database connected successfully...")
    except Exception as e:
        logger.error(e)
        raise e

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
