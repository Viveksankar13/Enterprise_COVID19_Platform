import logging
import sys
from typing import Any, Dict
import json
from datetime import datetime
from app.core.config import settings


class JSONFormatter(logging.Formatter):
    """
    Formatter that outputs JSON logs for production environments.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_payload: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
            "process": record.process,
            "thread": record.threadName,
        }
        if record.exc_info:
            log_payload["exception"] = self.formatException(record.exc_info)
        
        # Add extra custom attributes if present
        if hasattr(record, "extra") and isinstance(record.extra, dict): # type: ignore
            log_payload.update(record.extra) # type: ignore

        return json.dumps(log_payload)


def setup_logging() -> None:
    """
    Sets up application-wide logging configuration.
    Uses JSON formatting in production and readable color/standard logs in development.
    """
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
    logger = logging.getLogger()
    logger.setLevel(log_level)

    # Clear existing handlers
    logger.handlers.clear()

    # Stream Handler
    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(log_level)

    if settings.APP_ENV == "production":
        formatter = JSONFormatter()
    else:
        # Standard readable formatting for development
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s.%(funcName)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # Silence verbose 3rd party logs in info mode
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
