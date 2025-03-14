# test_ai_orchestration.py

import os
import sys
import json
import logging
import requests
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_ai_orchestration():
    """Test if the AI orchestration is working properly"""
    logger.info("Testing AI orchestration with a simple query...")
    
    # Base URL and endpoint
    base_url = "https://ai-orch-warrior-5ff152a0e1f8.herokuapp.com"
    endpoint = "/api/process"
    
    # Test query
    test_query = "Generate a short poem about technology"
    
    # Send request
    try:
        logger.info(f"Sending request to {base_url}{endpoint}")
        response = requests.post(
            f"{base_url}{endpoint}",
            json={
                "user_id": "test_orchestration_user",
                "message": test_query
            },
            timeout=60
        )
        
        logger.info(f"Response status: {response.status_code}")
        
        if response.status_code == 200:
            logger.info("Response body:")
            response_data = response.json()
            logger.info(json.dumps(response_data, indent=2))
            
            # Check if response contains "mock response"
            if "mock response" in response.text.lower():
                logger.warning("Response appears to be a mock response, not actual AI output")
                return False
            
            return True
        else:
            logger.error(f"Request failed: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Exception: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_ai_orchestration()
    sys.exit(0 if success else 1)
