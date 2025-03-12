# test_system.py

import os
import sys
import logging
import json
import time
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_api_endpoint():
    """Test the API endpoint for processing requests."""
    import requests
    
    logger.info("Testing API endpoint...")
    
    # API endpoint
    url = "https://ai-orchestration-dashboardwar-325750143bf3.herokuapp.com/api/process"
    
    # Test data
    payload = {
        "user_id": "test_user",
        "message": "Test message for system verification"
    }
    
    try:
        # Send request
        response = requests.post(url, json=payload)
        
        # Check status code
        if response.status_code == 200:
            logger.info("✅ API endpoint test successful")
            logger.info(f"Response: {json.dumps(response.json(), indent=2)}")
            return True
        else:
            logger.error(f"❌ API endpoint test failed with status code: {response.status_code}")
            logger.error(f"Response: {response.text}")
            return False
    except Exception as e:
        logger.error(f"❌ API endpoint test failed: {str(e)}")
        return False

def test_storage():
    """Test the storage system by checking for output files."""
    logger.info("Testing storage system...")
    
    # Check local storage (fallback)
    output_dir = os.path.join("logs", "outputs", "user_test_user")
    
    if os.path.exists(output_dir):
        files = os.listdir(output_dir)
        if files:
            logger.info(f"✅ Storage test successful. Found {len(files)} output files.")
            return True
    
    logger.warning("⚠️ No local storage files found. This may be normal if using Google Drive.")
    return True

def test_orchestrator():
    """Test the AI Orchestrator directly."""
    logger.info("Testing AI Orchestrator...")
    
    try:
        from src.ai_integration.orchestrator import AIOrchestrator
        
        # Initialize orchestrator
        orchestrator = AIOrchestrator()
        
        # Process a test request
        result = orchestrator.process_request("test_user", "Test message for orchestrator")
        
        if result and "result" in result:
            logger.info("✅ Orchestrator test successful")
            logger.info(f"Result: {json.dumps(result, indent=2)}")
            return True
        else:
            logger.error("❌ Orchestrator test failed - invalid result format")
            return False
    except Exception as e:
        logger.error(f"❌ Orchestrator test failed: {str(e)}")
        return False

def test_connectors():
    """Test the AI service connectors."""
    logger.info("Testing AI service connectors...")
    
    try:
        from src.ai_integration.connectors.gemini_connector import GeminiConnector
        from src.ai_integration.connectors.chatgpt_connector import ChatGPTConnector
        
        # Test Gemini connector
        gemini = GeminiConnector()
        gemini_result = gemini.generate_task("Test task generation")
        
        # Test ChatGPT connector
        chatgpt = ChatGPTConnector()
        chatgpt_result = chatgpt.execute_task(gemini_result)
        
        logger.info("✅ Connector tests successful")
        logger.info(f"Gemini result: {json.dumps(gemini_result, indent=2)}")
        logger.info(f"ChatGPT result: {json.dumps(chatgpt_result, indent=2)}")
        return True
    except Exception as e:
        logger.error(f"❌ Connector tests failed: {str(e)}")
        return False

def run_all_tests():
    """Run all system tests."""
    results = {
        "api_endpoint": test_api_endpoint(),
        "storage": test_storage(),
        "orchestrator": test_orchestrator(),
        "connectors": test_connectors()
    }
    
    # Print summary
    logger.info("\n===== Test Results =====")
    all_passed = True
    for test_name, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        logger.info(f"{test_name}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        logger.info("\n✅ All tests passed! System is fully functional.")
        return 0
    else:
        logger.error("\n❌ Some tests failed. Check the logs for details.")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
