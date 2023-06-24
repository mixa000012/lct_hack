# mypy: ignore-errors
import logging

from starlette_context import context


class ContextLogger(logging.Logger):
    def __init__(
        self,
        name: str = "fastapi._context",
        parent: logging.Logger = logging.root,
    ):
        super().__init__(name)
        self._internal_logger = logging.getLogger("fastapi.context")
        self.parent = parent

    # pylint: disable=too-many-arguments
    def _log(
        self,
        level,
        msg,
        args,
        exc_info=None,
        extra=None,
        stack_info=False,
        stacklevel=1,
    ):
        ctx = context.data
        trace_id = ctx.get("trace_id")
        if extra is None:
            extra = {}
        non_loggable_data = ["trace_id"]
        data_str = " ".join(
            f"{k}={ctx.get(k)}"
            for k in sorted(ctx.keys())
            if k not in non_loggable_data and not k.startswith("_")
        )
        extra.update(
            {
                "ctx": trace_id,
                "trace_id": trace_id,
                "data": data_str,
            }
        )

        return self._internal_logger._log(
            level=level,
            msg=msg,
            args=args,
            exc_info=exc_info,
            extra=extra,
            stack_info=stack_info,
            stacklevel=stacklevel,
        )
