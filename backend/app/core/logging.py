import logging
import logging.config
import json
from typing import Any, Dict
from app.config.loader import settings

class JSONFormatter(logging.Formatter):
    """
    Custom formatter outputting structured log records as JSON strings.
    """
    def format(self, record: logging.LogRecord) -> str:
        log_payload: Dict[str, Any] = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "line_number": record.lineno,
        }
        
        if record.exc_info:
            log_payload["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_payload)

def setup_logging() -> None:
    """
    Initializes standard and JSON loggers for the application.
    """
    logging_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": JSONFormatter,
                "datefmt": "%Y-%m-%dT%H:%M:%S%z"
            },
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.LOG_LEVEL.upper(),
                "formatter": "json" if settings.ENVIRONMENT == "production" else "standard",
                "stream": "ext://sys.stdout"
            }
        },
        "root": {
            "level": settings.LOG_LEVEL.upper(),
            "handlers": ["console"]
        }
    }
    
    logging.config.dictConfig(logging_config)
