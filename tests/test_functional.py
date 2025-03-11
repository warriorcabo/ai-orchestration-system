import sys
import os
import logging
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

def test_orchestrator_function():
    try:
        from src.ai_integration.orchestrator import AIOrchestrator
        logger.info('Creating orchestrator instance...')
        orchestrator = AIOrchestrator()
        logger.info('✓ Successfully created orchestrator instance')
        
        # Test a simple message process
        logger.info('Testing message processing...')
        response = orchestrator.process_message("test_user", "Hello, how does this AI orchestration system work?")
        logger.info(f'✓ Response received: {response[:100]}...')
        return True
    except Exception as e:
        logger.error(f'✗ Orchestrator test failed: {str(e)}')
        import traceback
        logger.error(traceback.format_exc())
        return False

if __name__ == '__main__':
    success = test_orchestrator_function()
    print(f"Functional test {'successful' if success else 'failed'}")
