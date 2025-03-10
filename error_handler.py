# error_handler.py
import os
import sys
import logging
import traceback
import datetime
import json
from typing import Dict, Any, Optional, List, Union

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class ErrorHandler:
    """Central error handling system for the AI orchestration system"""

    # Error severity levels
    SEVERITY = {
        "INFO": 0,
        "WARNING": 1,
        "ERROR": 2,
        "CRITICAL": 3
    }

    # Error categories
    CATEGORIES = {
        "API": "API-related errors",
        "AUTH": "Authentication errors",
        "DATA": "Data processing errors",
        "SYSTEM": "System errors",
        "USER": "User-related errors",
        "NETWORK": "Network errors",
        "UNKNOWN": "Unclassified errors"
    }

    def __init__(self):
        """Initialize the error handler"""
        # Path to store error logs
        self.log_dir = os.environ.get("ERROR_LOG_DIR", "logs")

        # Create log directory if it doesn't exist
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        # Critical error notification threshold
        self.notification_threshold = self.SEVERITY["ERROR"]

        # Error history (in-memory cache)
        self.error_history = []
        self.max_history_size = 100

# Global functions for easy access from other modules
_handler = ErrorHandler()

def log_error(module: str, message: str, exception: Optional[Exception] = None,
             severity: str = "ERROR", category: str = "UNKNOWN",
             metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Global function to log errors from any module"""
    try:
        # Get current timestamp
        timestamp = datetime.datetime.now().isoformat()

        # Get exception traceback if available
        tb = None
        if exception:
            tb = traceback.format_exception(type(exception), exception, exception.__traceback__)

        # Create error record
        error_record = {
            "timestamp": timestamp,
            "module": module,
            "message": message,
            "severity": severity,
            "category": category,
            "traceback": tb,
            "metadata": metadata or {}
        }

        # Log to the appropriate level
        log_level = getattr(logging, severity, logging.ERROR)
        logger.log(log_level, f"{module} - {message}")

        return error_record

    except Exception as e:
        # Failsafe logging if error handling itself fails
        sys.stderr.write(f"CRITICAL: Error in error handler: {str(e)}\n")
        return {
            "timestamp": datetime.datetime.now().isoformat(),
            "module": "error_handler",
            "message": f"Error in error handler: {str(e)}",
            "severity": "CRITICAL",
            "category": "SYSTEM"
        }

