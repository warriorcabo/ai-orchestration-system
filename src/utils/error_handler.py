# error_handler.py
import os
import logging
import datetime
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def log_error(module: str, error_message: str, user_id: Optional[str] = None, **kwargs) -> None:
    """Log an error to console and file"""
    logger.error(f"ERROR: {module} - {error_message}")
    
    # Print notification (for testing)
    print(f"NOTIFICATION: ERROR: Error in {module} - {error_message}")
    
    # In a full implementation, you would save this to a file or database
