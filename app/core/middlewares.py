import time
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.base import RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.responses import Response
from starlette_context import context

from app.api.v1.errors import CustomJSONResponseException
from app.core.logs.logger import ContextLogger

logger = ContextLogger()


class ContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        trace_id = uuid4().hex[:10]
        context["trace_id"] = trace_id

        response = await call_next(request)
        response.headers["X-Request-ID"] = trace_id

        return response


class LogMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        logger.info(
            "Request {method} {path}{query}".format(
                method=request.method,
                path=request.url.path,
                query="?" + request.url.query if request.url.query else "",
            )
        )
        start_time = time.time()

        response = await call_next(request)

        process_time = time.time() - start_time
        formatted_process_time = "{0:.6f}".format(process_time)
        logger.info(
            f"{request.client.host if request.client is not None else ''} -> {request.url.path} {response.status_code} {response.headers['content-length']} [{formatted_process_time}s]"  # noqa
        )

        return response


class ExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        try:
            response = await call_next(request)
        except CustomJSONResponseException as exc:
            return JSONResponse(
                status_code=exc.status_code,
                content={"message": exc.message},
            )

        return response
