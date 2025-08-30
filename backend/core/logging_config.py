"""
Logging configuration for ML Extractor
Provides environment-based logging setup
"""
import logging
import os
from pathlib import Path
from decouple import config

def setup_logging():
    """Configure logging based on environment"""
    debug_mode = config('DEBUG', default=False, cast=bool)
    level = logging.DEBUG if debug_mode else logging.INFO
    
    # Create logs directory if it doesn't exist
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Configure logging format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create handlers
    handlers = [logging.StreamHandler()]
    
    if not debug_mode:
        # Add file handler for production
        file_handler = logging.FileHandler(log_dir / 'app.log')
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)
    
    # Configure root logger
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )
    
    return logging.getLogger(__name__)

def get_logger(name: str):
    """Get a logger for the given module name"""
    return logging.getLogger(name)
