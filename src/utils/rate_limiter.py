# rate_limiter.py

import time
import logging
from collections import defaultdict
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class RateLimiter:
    """Simple rate limiter for API calls"""
    
    def __init__(self, limits: Dict[str, int] = None):
        """
        Initialize rate limiter with default limits
        
        Args:
            limits: Dictionary of service_name -> calls_per_minute
        """
        # Default rate limits (calls per minute)
        self.limits = limits or {
            "openai": 60,     # OpenAI default tier limit
            "gemini": 60,     # Google Gemini estimated limit
            "telegram": 30,   # Telegram bot API limit
            "google_drive": 60 # Google Drive API estimated limit
        }
        
        # Track request timestamps for each service
        self.request_history = defaultdict(list)
        
    def check_rate_limit(self, service_name: str) -> bool:
        """
        Check if a service has exceeded its rate limit
        
        Args:
            service_name: Name of the service to check
            
        Returns:
            True if request is allowed, False if rate limited
        """
        current_time = time.time()
        limit = self.limits.get(service_name, 30)  # Default to 30 requests per minute
        
        # Get request history for this service
        history = self.request_history[service_name]
        
        # Clean up history older than 1 minute
        one_minute_ago = current_time - 60
        history = [t for t in history if t > one_minute_ago]
        self.request_history[service_name] = history
        
        # Check if we've reached the limit
        if len(history) >= limit:
            logger.warning(f"Rate limit reached for {service_name}: {limit} requests per minute")
            return False
        
        # Add this request to history
        self.request_history[service_name].append(current_time)
        return True
    
    def wait_if_needed(self, service_name: str) -> float:
        """
        Wait if rate limit is reached and return wait time
        
        Args:
            service_name: Name of the service
            
        Returns:
            Time waited in seconds (0 if no wait needed)
        """
        if self.check_rate_limit(service_name):
            return 0
        
        # Calculate wait time
        history = self.request_history[service_name]
        if not history:
            return 0
        
        oldest_request = min(history)
        current_time = time.time()
        wait_time = 60 - (current_time - oldest_request) + 0.1  # Add 0.1s buffer
        
        if wait_time > 0:
            logger.info(f"Rate limit reached for {service_name}, waiting {wait_time:.2f} seconds")
            time.sleep(wait_time)
            
            # Add this request to history
            self.request_history[service_name].append(time.time())
            return wait_time
        
        # Add this request to history
        self.request_history[service_name].append(current_time)
        return 0

# Global instance for easy import
rate_limiter = RateLimiter()
