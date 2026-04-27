import logging
import os
import sys

from pythonjsonlogger.jsonlogger import JsonFormatter
from rich.logging import RichHandler

_STANDARD_LOG_FIELDS = frozenset(logging.LogRecord("", 0, "", 0, "", (), None).__dict__) | {"message"}


class _ExtraFieldsFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        msg = super().format(record)
        extras = {k: v for k, v in record.__dict__.items() if k not in _STANDARD_LOG_FIELDS}
        if extras:
            fields = "  ".join(f"{k}={v}" for k, v in extras.items())
            msg = f"{msg}  |  {fields}"
        return msg


def configure_logging() -> None:
    if os.getenv("LOG_FORMAT", "rich") == "json":
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(JsonFormatter("%(asctime)s %(name)s %(levelname)s %(message)s"))
    else:
        handler = RichHandler(rich_tracebacks=True, show_path=False, omit_repeated_times=False)
        handler.setFormatter(_ExtraFieldsFormatter())

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    root.addHandler(handler)
