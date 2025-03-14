# Check app routes
import os
import sys
import logging
import requests
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_api_endpoint():
    """Check the API endpoint for the correct route/method"""
    base_url = "https://ai-orch-warrior-5ff152a0e1f8.herokuapp.com"
    
    # Try different endpoints/methods
    endpoints = [
        "/api/process",
        "/api/request",
        "/process",
        "/request"
    ]
    
    for endpoint in endpoints:
        try:
            logger.info(f"Checking endpoint: {endpoint} (OPTIONS method)")
            response = requests.options(f"{base_url}{endpoint}")
            logger.info(f"Status: {response.status_code}")
            
            if hasattr(response, 'allow'):
                logger.info(f"Allowed methods: {response.headers.get('Allow')}")
        except Exception as e:
            logger.error(f"Error checking {endpoint}: {str(e)}")

if __name__ == "__main__":
    check_api_endpoint()
