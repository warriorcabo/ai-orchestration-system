# app.py - Main application entry point
import os
import logging
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Import modules
from src.telegram.telegram_bot import TelegramBotHandler
from src.ai_integration.ai_orchestrator import AIOrchestrator
from utils.error_handler import ErrorHandler

def main():
    """Main function to start the application"""
    try:
        logger.info("Starting AI Orchestration System")
        
        # Initialize the error handler
        error_handler = ErrorHandler()
        
        # Initialize the AI Orchestrator
        try:
            logger.info("Initializing AI Orchestrator...")
            orchestrator = AIOrchestrator()
            logger.info("AI Orchestrator initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize AI Orchestrator: {str(e)}")
            error_handler.log_error("main", f"AI Orchestrator initialization error: {str(e)}")
            return
        
        # Initialize and start the Telegram bot
        try:
            telegram_token = os.environ.get("TELEGRAM_TOKEN", "8183769729:AAEXc0x1BizumecFeTVkEzQ75GjXesTKM24")
            webhook_url = os.environ.get("WEBHOOK_URL", None)
            
            logger.info("Initializing Telegram bot...")
            bot = TelegramBotHandler(telegram_token, orchestrator)
            logger.info("Starting Telegram bot...")
            bot.start(webhook_url)
            
            logger.info("AI Orchestration System started successfully")
        except Exception as e:
            logger.error(f"Failed to start Telegram bot: {str(e)}")
            error_handler.log_error("main", f"Telegram bot startup error: {str(e)}")
    
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        if 'error_handler' in locals():
            error_handler.log_error("main", f"Startup error: {str(e)}")
        else:
            logging.error(f"Error handler not initialized. Error: {str(e)}")

if __name__ == "__main__":
    main()
