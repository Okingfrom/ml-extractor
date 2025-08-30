"""
Logging configuration for ML Extractor
Provides environment-based logging setup
"""
import logging
import os
from pathlib import Path
from decouple import config
from logging.handlers import RotatingFileHandler


def setup_logging():
    """Configure logging based on environment.

    This sets up:
    - a console stream handler (all environments)
    - an info-level file `logs/app.log` (rotation not required for small apps)
    - a rotating debug-level file `logs/debug.log` (captures DEBUG and above, rotates at 5MB)

    The debug file is always created so operators can inspect detailed traces in production
    without changing the global log level.
    """
    debug_mode = config('DEBUG', default=False, cast=bool)
    level = logging.DEBUG if debug_mode else logging.INFO

    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(parents=True, exist_ok=True)

    # Configure logging format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)

    handlers = [console_handler]

    # Info-level file for general logs
    info_file = logging.FileHandler(log_dir / 'app.log')
    info_file.setLevel(logging.INFO)
    info_file.setFormatter(formatter)
    handlers.append(info_file)

    # Rotating debug file to capture detailed traces (always present)
    debug_file = RotatingFileHandler(log_dir / 'debug.log', maxBytes=5 * 1024 * 1024, backupCount=5)
    debug_file.setLevel(logging.DEBUG)
    debug_file.setFormatter(formatter)
    handlers.append(debug_file)

    # Configure root logger
    logging.basicConfig(level=level, handlers=handlers)

    return logging.getLogger(__name__)


def get_logger(name: str):
    """Get a logger for the given module name"""
    return logging.getLogger(name)
