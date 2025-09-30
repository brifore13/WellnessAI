"""
Logging configuration for the application.
Provides structured logging with different levels and formats.
"""
import logging
import sys
from typing import Dict, Any
import json
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """Custom formatter for JSON structured logs"""

    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }

        # Add exception info if present
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)

        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_entry["user_id"] = record.user_id

        return json.dumps(log_entry)

    def setup_logging(debug: bool = False) -> None:
        """
        Configure application logging
        Args:
            debug: If True, set log level to DEBUG and use console formatter
        """
        # Root logger configuration
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG if debug else logging.INFO)

        # Remove existing handlers
        for handler in root_logger.handlers[:]:
            root_logger.removeHandler(handler)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)

        if debug:
            # format for development
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
        else:
            # JSON format for production
            formatter = JSONFormatter()

        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

        # Set third-party library log levels
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("asyncpg").setLevel(logging.WARNING)
        logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance for a module."""
    return logging.getLogger(name)
