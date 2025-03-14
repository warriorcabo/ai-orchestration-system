"""Quick test of basic functionality."""
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Test imports
logger.info("Testing imports...")
try:
    import telegram
    logger.info("Telegram import successful")
except ImportError as e:
    logger.error(f"Telegram import failed: {e}")

try:
    import openai
    logger.info("OpenAI import successful")
except ImportError as e:
    logger.error(f"OpenAI import failed: {e}")

try:
    import google.generativeai as genai
    logger.info("Google Generative AI import successful")
except ImportError as e:
    logger.error(f"Google Generative AI import failed: {e}")

# Check environment variables
logger.info("Checking environment variables...")
for var in ["TELEGRAM_TOKEN", "OPENAI_API_KEY", "GEMINI_API_KEY", "GOOGLE_DRIVE_FOLDER_ID"]:
    value = os.environ.get(var)
    if value:
        logger.info(f"{var} is set to: {value[:5]}...")
    else:
        logger.warning(f"{var} is not set")

logger.info("Basic test completed")
