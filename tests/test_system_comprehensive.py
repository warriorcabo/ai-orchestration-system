import sys
import os
import logging
import time
import json
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
load_dotenv()

def run_comprehensive_test():
    """Run a comprehensive test of all system components"""
    test_results = {
        "component_initialization": {},
        "api_connectivity": {},
        "orchestration": {},
        "error_handling": {}
    }
    
    # Step 1: Test component initialization
    try:
        logger.info("Testing component initialization...")
        
        # Test error handler
        logger.info("Testing error handler...")
        from src.utils.error_handler import log_error
        test_results["component_initialization"]["error_handler"] = True
        
        # Test Gemini connector
        logger.info("Testing Gemini connector...")
        from src.ai_integration.gemini_connector import GeminiConnector
        gemini = GeminiConnector()
        test_results["component_initialization"]["gemini"] = True
        
        # Test ChatGPT connector
        logger.info("Testing ChatGPT connector...")
        from src.ai_integration.chatgpt_connector import ChatGPTConnector
        chatgpt = ChatGPTConnector()
        test_results["component_initialization"]["chatgpt"] = True
        
        # Test orchestrator
        logger.info("Testing orchestrator...")
        from src.ai_integration.orchestrator import AIOrchestrator
        orchestrator = AIOrchestrator()
        test_results["component_initialization"]["orchestrator"] = True
        
        # Test for Telegram bot (optional)
        try:
            logger.info("Testing Telegram bot (optional)...")
            from src.telegram.telegram_bot import TelegramBotHandler
            test_results["component_initialization"]["telegram_bot"] = True
        except Exception as e:
            logger.warning(f"Telegram bot not available: {str(e)}")
            test_results["component_initialization"]["telegram_bot"] = False
        
    except Exception as e:
        logger.error(f"Component initialization error: {str(e)}")
        return test_results
    
    # Step 2: Test API connectivity
    try:
        logger.info("Testing API connectivity...")
        
        # Test Gemini API
        logger.info("Testing Gemini API...")
        gemini_response = gemini.generate_response("This is a test")
        test_results["api_connectivity"]["gemini"] = True if gemini_response and len(gemini_response) > 10 else False
        logger.info(f"Gemini response: {gemini_response[:100]}...")
        
        # Test ChatGPT API
        logger.info("Testing ChatGPT API...")
        chatgpt_response = chatgpt.generate_response("This is a test")
        test_results["api_connectivity"]["chatgpt"] = True if chatgpt_response and len(chatgpt_response) > 10 else False
        logger.info(f"ChatGPT response: {chatgpt_response[:100]}...")
        
    except Exception as e:
        logger.error(f"API connectivity error: {str(e)}")
    
    # Step 3: Test orchestration
    try:
        logger.info("Testing orchestration...")
        
        # Test basic query
        logger.info("Testing basic query...")
        basic_response = orchestrator.process_message("test_user", "What is AI orchestration?")
        test_results["orchestration"]["basic_query"] = True if basic_response and len(basic_response) > 50 else False
        logger.info(f"Basic query response: {basic_response[:100]}...")
        
        # Test complex query
        logger.info("Testing complex query...")
        complex_response = orchestrator.process_message("test_user", "Compare neural networks and decision trees for classification tasks.")
        test_results["orchestration"]["complex_query"] = True if complex_response and len(complex_response) > 200 else False
        logger.info(f"Complex query response received: {len(complex_response)} characters")
        
    except Exception as e:
        logger.error(f"Orchestration error: {str(e)}")
    
    # Step 4: Test error handling
    try:
        logger.info("Testing error handling...")
        
        # Test error logging
        logger.info("Testing error logging...")
        log_error("test_module", "This is a test error")
        test_results["error_handling"]["error_logging"] = True
        
    except Exception as e:
        logger.error(f"Error handling test error: {str(e)}")
    
    # Print overall test results
    logger.info("\n\n=== TEST RESULTS SUMMARY ===")
    for category, tests in test_results.items():
        logger.info(f"\n{category.upper()}:")
        for test, result in tests.items():
            status = "✓ PASSED" if result else "✗ FAILED"
            logger.info(f"  {status}: {test}")
    
    # Check if all critical tests passed
    critical_tests = [
        test_results["component_initialization"].get("error_handler", False),
        test_results["component_initialization"].get("gemini", False),
        test_results["component_initialization"].get("chatgpt", False),
        test_results["component_initialization"].get("orchestrator", False),
        test_results["api_connectivity"].get("gemini", False),
        test_results["api_connectivity"].get("chatgpt", False),
        test_results["orchestration"].get("basic_query", False)
    ]
    
    all_critical_passed = all(critical_tests)
    logger.info(f"\nCRITICAL TESTS: {'ALL PASSED' if all_critical_passed else 'SOME FAILED'}")
    logger.info(f"SYSTEM STATUS: {'OPERATIONAL' if all_critical_passed else 'NEEDS ATTENTION'}")
    
    return test_results

if __name__ == "__main__":
    logger.info("Starting comprehensive system test...")
    run_comprehensive_test()
    logger.info("Test completed.")
