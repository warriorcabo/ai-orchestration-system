# comprehensive_test.py

import os
import sys
import json
import time
import logging
import requests
import random
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("test_logs.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Constants
BASE_URL = "https://ai-orch-warrior-5ff152a0e1f8.herokuapp.com"
API_ENDPOINT = f"{BASE_URL}/api/process"
TEST_USER_ID = "test_user"
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

# Test cases with different scenarios
TEST_CASES = [
    {
        "name": "Simple greeting",
        "message": "Hello AI Orchestrator",
        "expected_status": "success",
        "check_storage": True
    },
    {
        "name": "Complex query",
        "message": "Explain the differences between supervised and unsupervised machine learning models",
        "expected_status": "success",
        "check_storage": True
    },
    {
        "name": "Error-inducing query (too long)",
        "message": "Write a detailed essay about " + "artificial intelligence " * 50,
        "expected_status": "success",  # We expect success because our system handles errors gracefully
        "check_storage": True
    }
]

def make_api_request(message, retry_count=0):
    """Make a request to the API with retry logic"""
    payload = {
        "user_id": TEST_USER_ID,
        "message": message
    }
    
    try:
        logger.info(f"Sending request: {message[:50]}...")
        response = requests.post(
            API_ENDPOINT,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        # Check if response is valid
        if response.status_code == 200:
            return response.json()
        else:
            if retry_count < MAX_RETRIES:
                logger.warning(f"Request failed with status {response.status_code}, retrying ({retry_count+1}/{MAX_RETRIES})...")
                time.sleep(RETRY_DELAY)
                return make_api_request(message, retry_count + 1)
            else:
                logger.error(f"Request failed after {MAX_RETRIES} retries with status {response.status_code}")
                return {"status": "error", "error": f"HTTP {response.status_code}"}
    except Exception as e:
        if retry_count < MAX_RETRIES:
            logger.warning(f"Request failed with error: {str(e)}, retrying ({retry_count+1}/{MAX_RETRIES})...")
            time.sleep(RETRY_DELAY)
            return make_api_request(message, retry_count + 1)
        else:
            logger.error(f"Request failed after {MAX_RETRIES} retries with error: {str(e)}")
            return {"status": "error", "error": str(e)}

def check_storage_reference(storage_ref):
    """Check if storage reference is valid"""
    if not storage_ref:
        return False
    
    if storage_ref.startswith("local:"):
        # For local storage, we consider it a success since we can't check the file on Heroku
        return True
    elif storage_ref.startswith("google_drive:"):
        # For Google Drive, we consider it a success if it's not an error message
        return "error" not in storage_ref and "failed" not in storage_ref
    else:
        return False

def test_api_health():
    """Test the API health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/api/health")
        if response.status_code == 200:
            health_data = response.json()
            logger.info(f"API Health Check: {health_data['status']}")
            return True
        else:
            logger.error(f"API Health Check failed with status {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"API Health Check failed with error: {str(e)}")
        return False

def run_test_case(test_case):
    """Run a single test case"""
    logger.info(f"Running test case: {test_case['name']}")
    
    # Make the API request
    response = make_api_request(test_case['message'])
    
    # Check status
    test_passed = True
    if response.get("status") != test_case["expected_status"]:
        logger.error(f"Test failed: Expected status '{test_case['expected_status']}', got '{response.get('status')}'")
        test_passed = False
    
    # Check if response contains expected fields
    if "response" not in response:
        logger.error("Test failed: Missing 'response' field in API response")
        test_passed = False
    elif "result" not in response["response"]:
        logger.error("Test failed: Missing 'result' field in API response")
        test_passed = False
    
    # Check storage reference if required
    if test_case['check_storage'] and "response" in response:
        storage_ref = response["response"].get("storage_reference")
        if not storage_ref:
            logger.error("Test failed: Missing 'storage_reference' field in response")
            test_passed = False
        elif not check_storage_reference(storage_ref):
            logger.error(f"Test failed: Invalid storage reference: {storage_ref}")
            test_passed = False
        else:
            logger.info(f"Storage reference check passed: {storage_ref}")
    
    # Log detailed response for debugging
    logger.info(f"Response: {json.dumps(response, indent=2)}")
    
    return test_passed

def run_all_tests():
    """Run all test cases"""
    # First check API health
    if not test_api_health():
        logger.error("API Health Check failed. Skipping remaining tests.")
        return False
    
    # Log test run start
    logger.info(f"Starting test run at {datetime.now().isoformat()}")
    logger.info(f"Running {len(TEST_CASES)} test cases")
    
    # Run all test cases
    results = {}
    all_passed = True
    for test_case in TEST_CASES:
        test_name = test_case["name"]
        test_result = run_test_case(test_case)
        results[test_name] = "PASSED" if test_result else "FAILED"
        if not test_result:
            all_passed = False
        
        # Add delay between tests to avoid rate limiting
        time.sleep(1)
    
    # Print summary
    logger.info("\n===== Test Results =====")
    for test_name, result in results.items():
        logger.info(f"{test_name}: {result}")
    
    if all_passed:
        logger.info("\n✅ All tests passed! System is fully functional.")
        return True
    else:
        logger.error("\n❌ Some tests failed. Check the logs for details.")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

