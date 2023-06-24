import logging
import logging.config
import os
import sys
from logging.handlers import RotatingFileHandler
from typing import Literal, Mapping


class GenericFormatter(logging.Formatter):
    FORMAT = (
        "%(created)f %(asctime)s.%(msecs)03d [%(process)d] [%(taskid)d] "
        "[%(name)s::%(module)s:%(funcName)s:%(lineno)d] "
        "%(levelname)s: %(message)s"
    )
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    def __init__(
        self,
        fmt: str | None = None,
        datefmt: str | None = None,
        style: Literal["%", "{", "$"] = "%",
    ) -> None:
        super().__init__(fmt or self.FORMAT, datefmt or self.DATE_FORMAT, style)

    def formatMessage(self, record: logging.LogRecord) -> str:
        record.taskid = 0
        try:
            import asyncio

            task = asyncio.current_task()
            if task is not None:
                record.taskid = id(task)
        except (ImportError, RuntimeError):
            pass
        return super().formatMessage(record)


class ContextFormatter(GenericFormatter):
    FORMAT = (
        "%(created)f %(asctime)s.%(msecs)03d [%(process)d] [%(taskid)d] "
        "[%(name)s::%(module)s:%(funcName)s:%(lineno)d] "
        "[ trace_id=%(trace_id)s %(data)s ] %(levelname)s: %(message)s"  # noqa
    )


def setup_logging(
    *,
    log_path: str | None = None,
    loggers: Mapping | None = None,
    log_level: int = logging.DEBUG,
    log_stderr: bool = True,
    generic_formatter: logging.Formatter | None = None,
    ctx_formatter: logging.Formatter | None = None,
) -> None:
    generic_formatter = generic_formatter or GenericFormatter()
    ctx_formatter = ctx_formatter or ContextFormatter()

    console_handler = None
    console_ctx_handler = None
    if log_stderr:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(generic_formatter)

        console_ctx_handler = logging.StreamHandler(sys.stderr)
        console_ctx_handler.setLevel(log_level)
        console_ctx_handler.setFormatter(ctx_formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)
    if console_handler:
        root_logger.addHandler(console_handler)

    context_logger = logging.getLogger("fastapi.context")
    context_logger.propagate = False
    context_logger.setLevel(log_level)
    if console_ctx_handler:
        context_logger.addHandler(console_ctx_handler)

    if log_path is not None:
        log_path = os.path.abspath(log_path)
        log_path_parent = os.path.dirname(log_path)

        if not os.path.exists(log_path_parent):
            raise ValueError(f"Path {log_path_parent} does no exist")

        file_handler = RotatingFileHandler(filename=log_path)
        file_handler.setLevel(log_level)
        file_handler.setFormatter(generic_formatter)
        root_logger.addHandler(file_handler)

        file_ctx_handler = RotatingFileHandler(filename=log_path)
        file_ctx_handler.setLevel(log_level)
        file_ctx_handler.setFormatter(ctx_formatter)
        context_logger.addHandler(file_ctx_handler)

    if loggers is None:
        loggers = {}

    loggers = {
        "asyncio": {
            "level": "WARN",
            "propagate": True,
            "qualname": "asyncio",
        },
        **loggers,
    }
    logging.getLogger("uvicorn.access").handlers = []
    logging.getLogger("uvicorn.access").propagate = False
    logging.config.dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "loggers": loggers,
        }
    )
