# test_components.py

import logging
import sys
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_gemini_connector():
    """Test the Gemini connector."""
    from src.ai_integration.connectors.gemini_connector import GeminiConnector
    
    logger.info("Testing Gemini connector...")
    gemini = GeminiConnector()
    
    try:
        task = gemini.generate_task("Write a short poem about AI")
        logger.info(f"Gemini task generation successful: {task}")
        return True
    except Exception as e:
        logger.error(f"Gemini connector test failed: {str(e)}")
        return False

def test_chatgpt_connector():
    """Test the ChatGPT connector."""
    from src.ai_integration.connectors.chatgpt_connector import ChatGPTConnector
    
    logger.info("Testing ChatGPT connector...")
    chatgpt = ChatGPTConnector()
    
    try:
        task = {
            "task_type": "text_generation",
            "instructions": "Write a short poem about AI"
        }
        result = chatgpt.execute_task(task)
        logger.info(f"ChatGPT task execution successful: {result}")
        return True
    except Exception as e:
        logger.error(f"ChatGPT connector test failed: {str(e)}")
        return False

def test_error_handler():
    """Test the error handler."""
    from src.utils.error_handler import log_error
    
    logger.info("Testing error handler...")
    try:
        error_record = log_error("test_module", "This is a test error", severity="INFO")
        logger.info(f"Error handler test successful: {error_record}")
        return True
    except Exception as e:
        logger.error(f"Error handler test failed: {str(e)}")
        return False

def test_feedback_loop_manager():
    """Test the feedback loop manager."""
    from src.utils.feedback_loop_manager import FeedbackLoopManager
    
    logger.info("Testing feedback loop manager...")
    try:
        manager = FeedbackLoopManager()
        
        # Mock functions for testing
        def mock_review(response, query):
            return "This needs improvement"
        
        def mock_revision(response, feedback, query):
            return response + " (improved)"
        
        result, history = manager.process_feedback_loop(
            "test_conversation",
            "Test query",
            "Initial response",
            mock_review,
            mock_revision
        )
        
        logger.info(f"Feedback loop test successful: {result}")
        return True
    except Exception as e:
        logger.error(f"Feedback loop test failed: {str(e)}")
        return False

def test_orchestrator():
    """Test the AI orchestrator."""
    from src.ai_integration.orchestrator import AIOrchestrator
    
    logger.info("Testing AI orchestrator...")
    try:
        orchestrator = AIOrchestrator()
        result = orchestrator.process_request("test_user", "Hello, this is a test message")
        logger.info(f"Orchestrator test successful: {result}")
        return True
    except Exception as e:
        logger.error(f"Orchestrator test failed: {str(e)}")
        return False

def run_all_tests():
    """Run all component tests."""
    results = {
        "gemini_connector": test_gemini_connector(),
        "chatgpt_connector": test_chatgpt_connector(),
        "error_handler": test_error_handler(),
        "feedback_loop_manager": test_feedback_loop_manager(),
        "orchestrator": test_orchestrator()
    }
    
    logger.info("===== Test Results =====")
    all_passed = True
    for component, passed in results.items():
        status = "PASSED" if passed else "FAILED"
        logger.info(f"{component}: {status}")
        if not passed:
            all_passed = False
    
    if all_passed:
        logger.info("All components working correctly!")
        return 0
    else:
        logger.error("Some components failed testing.")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests())
