# single_request_test.py

import os
import sys
import json
import logging
import requests
import time
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_single_request():
    """Test a single request to the AI orchestration system"""
    logger.info("Testing a single request to the AI orchestration system...")
    
    # Base URL and endpoint
    base_url = "https://ai-orch-warrior-5ff152a0e1f8.herokuapp.com"
    endpoint = "/api/process"
    
    # Test query
    test_query = "What is machine learning? Give a brief explanation."
    
    # Send request
    try:
        logger.info(f"Sending request to {base_url}{endpoint}")
        start_time = time.time()
        
        response = requests.post(
            f"{base_url}{endpoint}",
            json={
                "user_id": "single_test_user",
                "message": test_query
            },
            timeout=120
        )
        
        elapsed_time = time.time() - start_time
        logger.info(f"Response received in {elapsed_time:.2f} seconds")
        logger.info(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            response_data = response.json()
            logger.info("Response data (truncated):")
            logger.info(json.dumps(response_data, indent=2)[:500] + "...")
            
            # Check if it's a mock response
            if "mock response" in json.dumps(response_data).lower():
                logger.warning("Received a mock response - AI integration not working correctly")
            else:
                logger.info("Received an actual AI-generated response")
                
            return True
        else:
            logger.error(f"Request failed: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Exception: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_single_request()
    sys.exit(0 if success else 1)
