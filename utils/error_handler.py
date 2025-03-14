# error_handler.py
import os
import sys
import logging
import traceback
import datetime
import json
import time
from typing import Dict, Any, Optional, List, Union

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("error_logs.log"),
        logging.StreamHandler(sys.stdout)
    ]
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
        
        logger.info("Error Handler initialized")

    def log_error(self, module: str, message: str, exception: Optional[Exception] = None,
                severity: str = "ERROR", category: str = "UNKNOWN",
                metadata: Optional[Dict[str, Any]] = None, user_id: Optional[str] = None) -> Dict[str, Any]:
        """Log an error with detailed information"""
        try:
            # Get current timestamp
            timestamp = datetime.datetime.now().isoformat()

            # Get exception traceback if available
            tb = None
            if exception:
                tb = "".join(traceback.format_exception(type(exception), exception, exception.__traceback__))

            # Create error record
            error_record = {
                "timestamp": timestamp,
                "module": module,
                "message": message,
                "severity": severity,
                "category": category,
                "traceback": tb,
                "user_id": user_id,
                "metadata": metadata or {}
            }

            # Log to the appropriate level
            log_level = getattr(logging, severity, logging.ERROR)
            if user_id:
                logger.log(log_level, f"{module} - {message} (User: {user_id})")
            else:
                logger.log(log_level, f"{module} - {message}")

            # Add to in-memory history
            self._add_to_history(error_record)

            # Write to JSON log file
            self._write_to_log_file(error_record)

            # Send notification if needed
            if self.SEVERITY.get(severity, 0) >= self.notification_threshold:
                self._send_notification(error_record)

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

    def _write_to_log_file(self, error_record: Dict[str, Any]) -> None:
        """Write error record to a JSON log file"""
        try:
            # Create filename based on date
            date_str = datetime.datetime.now().strftime("%Y-%m-%d")
            log_filename = os.path.join(self.log_dir, f"errors_{date_str}.json")

            # Append to the log file
            with open(log_filename, 'a') as f:
                f.write(json.dumps(error_record) + "\n")

        except Exception as e:
            sys.stderr.write(f"CRITICAL: Failed to write to error log file: {str(e)}\n")

    def _add_to_history(self, error_record: Dict[str, Any]) -> None:
        """Add error record to in-memory history"""
        self.error_history.append(error_record)

        # Trim history if it exceeds maximum size
        if len(self.error_history) > self.max_history_size:
            self.error_history = self.error_history[-self.max_history_size:]

    def _send_notification(self, error_record: Dict[str, Any]) -> None:
        """Send notification for critical errors"""
        try:
            # Format notification message
            module = error_record.get("module", "unknown")
            message = error_record.get("message", "Unknown error")
            severity = error_record.get("severity", "ERROR")
            user_id = error_record.get("user_id", "unknown")

            notification_message = f"{severity}: Error in {module} - {message}"
            if user_id != "unknown":
                notification_message += f" (User: {user_id})"

            # Log notification
            logger.info(f"Sending notification: {notification_message}")

            # For now, just print to stderr since we don't have notification service integrated
            sys.stderr.write(f"NOTIFICATION: {notification_message}\n")

        except Exception as e:
            sys.stderr.write(f"CRITICAL: Failed to send notification: {str(e)}\n")

    def classify_error(self, error_message: str) -> Dict[str, str]:
        """Classify an error based on its message"""
        # API error classification
        if any(term in error_message.lower() for term in ["api", "request", "response", "status", "endpoint"]):
            return {"category": "API"}

        # Authentication error classification
        if any(term in error_message.lower() for term in ["auth", "token", "credential", "permission", "access denied"]):
            return {"category": "AUTH"}

        # Network error classification
        if any(term in error_message.lower() for term in ["network", "connection", "timeout", "unreachable", "ssl"]):
            return {"category": "NETWORK"}

        # Data error classification
        if any(term in error_message.lower() for term in ["data", "parse", "format", "json", "value"]):
            return {"category": "DATA"}

        # User error classification
        if any(term in error_message.lower() for term in ["user", "input", "request", "parameter"]):
            return {"category": "USER"}

        # Default classification
        return {"category": "UNKNOWN"}

# Global functions for easy access from other modules
_handler = ErrorHandler()

def log_error(module: str, message: str, exception: Optional[Exception] = None,
             severity: str = "ERROR", category: str = "UNKNOWN",
             metadata: Optional[Dict[str, Any]] = None, user_id: Optional[str] = None) -> Dict[str, Any]:
    """Global function to log errors from any module"""
    global _handler
    return _handler.log_error(
        module, message, exception, severity, category, metadata, user_id
    )

def handle_exception(module: str, exc: Exception, metadata: Optional[Dict[str, Any]] = None, 
                    user_id: Optional[str] = None) -> Dict[str, Any]:
    """Handle an exception with appropriate logging and classification"""
    global _handler
    # Get error message
    message = str(exc)

    # Classify the error
    classification = _handler.classify_error(message)
    category = classification.get("category", "UNKNOWN")

    # Determine severity based on exception type
    severity = "ERROR"
    if isinstance(exc, (KeyError, ValueError, TypeError)):
        severity = "WARNING"

    # Log the error
    return log_error(
        module=module,
        message=message,
        exception=exc,
        severity=severity,
        category=category,
        metadata=metadata,
        user_id=user_id
    )
