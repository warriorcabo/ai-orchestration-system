import sys
import os
import logging

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Add current directory to path
sys.path.insert(0, os.getcwd())

try:
    from src.ai_integration.gemini_connector import GeminiConnector
    logger.info("Successfully imported GeminiConnector!")
except Exception as e:
    logger.error(f"Failed to import GeminiConnector: {str(e)}")
