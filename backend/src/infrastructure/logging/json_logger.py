"""
JSON Logging Configuration.

Configures structured JSON logging for better observability.
Logs include correlation IDs, timestamps, and structured data.
"""
import logging
import sys
import json
from datetime import datetime
from typing import Any, Dict
import uuid
from contextvars import ContextVar

# Context variable for correlation ID
correlation_id_var: ContextVar[str] = ContextVar('correlation_id', default='')


def get_correlation_id() -> str:
    """Get or generate a correlation ID for request tracing."""
    cid = correlation_id_var.get()
    if not cid:
        cid = str(uuid.uuid4())[:8]
        correlation_id_var.set(cid)
    return cid


def set_correlation_id(cid: str) -> None:
    """Set correlation ID for current context."""
    correlation_id_var.set(cid)


class JSONFormatter(logging.Formatter):
    """
    Custom JSON log formatter.
    
    Outputs logs in JSON format with:
    - timestamp (ISO 8601)
    - level
    - message
    - correlation_id
    - logger name
    - extra fields
    """
    
    def format(self, record: logging.LogRecord) -> str:
        log_dict: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": get_correlation_id(),
        }
        
        # Add location info for errors
        if record.levelno >= logging.ERROR:
            log_dict["location"] = {
                "file": record.filename,
                "line": record.lineno,
                "function": record.funcName,
            }
        
        # Add exception info if present
        if record.exc_info:
            log_dict["exception"] = self.formatException(record.exc_info)
        
        # Add any extra fields
        if hasattr(record, 'extra_data'):
            log_dict["data"] = record.extra_data
        
        return json.dumps(log_dict, default=str)


class StandardFormatter(logging.Formatter):
    """Human-readable formatter for development."""
    
    def format(self, record: logging.LogRecord) -> str:
        cid = get_correlation_id()
        prefix = f"[{cid}] " if cid else ""
        return f"{record.levelname} {prefix}{record.name}: {record.getMessage()}"


def configure_logging(
    json_format: bool = True,
    level: int = logging.INFO,
    log_to_file: str = None
) -> None:
    """
    Configure application logging.
    
    Args:
        json_format: Use JSON format (True) or human-readable (False)
        level: Logging level (default INFO)
        log_to_file: Optional file path for log output
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Clear existing handlers
    root_logger.handlers.clear()
    
    # Choose formatter
    if json_format:
        formatter = JSONFormatter()
    else:
        formatter = StandardFormatter()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_to_file:
        file_handler = logging.FileHandler(log_to_file)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Quiet noisy libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name."""
    return logging.getLogger(name)
