import logging
import time
import os
from typing import Optional, Dict, Any

# Configure logging level from environment
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
logging.basicConfig(level=getattr(logging, LOG_LEVEL, logging.INFO))

logger = logging.getLogger('ml-extractor')

def timed(label: str):
    """
    Returns a timing closure for logging operation duration.
    
    Usage:
        stop = timed("processing records")
        # ... do work ...
        stop({"count": 5})  # logs: "processing records completed in 0.123s (count=5)"
    """
    start_time = time.time()
    
    def stop(extra: Optional[Dict[str, Any]] = None):
        duration = time.time() - start_time
        extra_str = ""
        if extra:
            extra_parts = [f"{k}={v}" for k, v in extra.items()]
            extra_str = f" ({', '.join(extra_parts)})"
        
        logger.debug(f"{label} completed in {duration:.3f}s{extra_str}")
    
    return stop
