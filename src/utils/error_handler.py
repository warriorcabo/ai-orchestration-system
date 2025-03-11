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

    def log_error(self, module: str, message: str, exception: Optional[Exception] = None,
                severity: str = "ERROR", category: str = "UNKNOWN",
                metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Log an error with detailed information"""
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

            notification_message = f"{severity}: Error in {module} - {message}"

            # Log notification
            logger.info(f"Sending notification: {notification_message}")

            # TODO: Implement actual notification sending
            # This could connect to Telegram, email, Slack, etc.
            # For now, just print to stderr
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
        if any(term in error_message.lower() for term in ["network", "connection", "timeout", "unreachable"]):
            return {"category": "NETWORK"}

        # Data error classification
        if any(term in error_message.lower() for term in ["data", "parse", "format", "json", "value"]):
            return {"category": "DATA"}

        # User error classification
        if any(term in error_message.lower() for term in ["user", "input", "request", "parameter"]):
            return {"category": "USER"}

        # Default classification
        return {"category": "UNKNOWN"}

    def get_error_stats(self, time_period: Optional[str] = None) -> Dict[str, Any]:
        """Get error statistics for a specified time period"""
        # Filter errors by time if specified
        filtered_errors = self.error_history

        if time_period:
            # Get cutoff time
            now = datetime.datetime.now()
            if time_period == "hour":
                cutoff = now - datetime.timedelta(hours=1)
            elif time_period == "day":
                cutoff = now - datetime.timedelta(days=1)
            elif time_period == "week":
                cutoff = now - datetime.timedelta(weeks=1)
            else:
                cutoff = datetime.datetime.min

            # Filter by timestamp
            filtered_errors = [
                e for e in self.error_history
                if datetime.datetime.fromisoformat(e["timestamp"]) > cutoff
            ]

        # Count by category
        category_counts = {}
        for e in filtered_errors:
            category = e.get("category", "UNKNOWN")
            category_counts[category] = category_counts.get(category, 0) + 1

        # Count by module
        module_counts = {}
        for e in filtered_errors:
            module = e.get("module", "unknown")
            module_counts[module] = module_counts.get(module, 0) + 1

        # Count by severity
        severity_counts = {}
        for e in filtered_errors:
            severity = e.get("severity", "UNKNOWN")
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        return {
            "total": len(filtered_errors),
            "by_category": category_counts,
            "by_module": module_counts,
            "by_severity": severity_counts,
            "time_period": time_period
        }

    def suggest_recovery(self, error_record: Dict[str, Any]) -> str:
        """Suggest recovery actions for common errors"""
        category = error_record.get("category", "UNKNOWN")
        message = error_record.get("message", "").lower()

        # API errors
        if category == "API":
            if "rate limit" in message or "too many requests" in message:
                return "Implement exponential backoff and retry after a delay"
            if "timeout" in message:
                return "Check API endpoint health and retry with increased timeout"

        # Authentication errors
        if category == "AUTH":
            if "expired" in message:
                return "Refresh authentication tokens"
            if "invalid" in message:
                return "Verify API keys and credentials"

        # Network errors
        if category == "NETWORK":
            return "Check network connectivity and retry the operation"

        # Data errors
        if category == "DATA":
            if "parse" in message or "json" in message:
                return "Validate input data format before processing"

        # Default suggestion
        return "Review logs and check module documentation for troubleshooting steps"


# Global functions for easy access from other modules
_handler = ErrorHandler()

def log_error(module: str, message: str, exception: Optional[Exception] = None,
            severity: str = "ERROR", category: str = "UNKNOWN",
            metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Global function to log errors from any module"""
    return _handler.log_error(
        module, message, exception, severity, category, metadata
    )

def get_error_stats(time_period: Optional[str] = None) -> Dict[str, Any]:
    """Global function to get error statistics"""
    return _handler.get_error_stats(time_period)

def handle_exception(module: str, exc: Exception, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Handle an exception with appropriate logging and classification"""
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
        metadata=metadata
    )
