import sys
import os
import logging

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_imports():
    try:
        logger.info('Testing error_handler import...')
        from src.utils.error_handler import log_error
        logger.info('✓ Successfully imported error_handler')
        
        logger.info('Testing gemini_connector import...')
        from src.ai_integration.gemini_connector import GeminiConnector
        logger.info('✓ Successfully imported gemini_connector')
        
        logger.info('Testing chatgpt_connector import...')
        from src.ai_integration.chatgpt_connector import ChatGPTConnector
        logger.info('✓ Successfully imported chatgpt_connector')
        
        logger.info('Testing orchestrator import...')
        from src.ai_integration.orchestrator import AIOrchestrator
        logger.info('✓ Successfully imported orchestrator')
        
        return True
    except Exception as e:
        logger.error(f'Import error: {str(e)}')
        return False

if __name__ == '__main__':
    success = test_imports()
    print(f"Import test {'successful' if success else 'failed'}")
