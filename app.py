import os
import sys
import logging
import traceback
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Add the current directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

def main():
    """Main entry point for the AI Orchestration System"""
    try:
        logger.info("Starting AI Orchestration System")
        
        # Import the required modules
        from src.ai_integration.orchestrator import AIOrchestrator
        
        # Initialize the orchestrator
        orchestrator = AIOrchestrator()
        logger.info("AI Orchestrator initialized successfully")
        
        # Check if we should initialize the Telegram bot
        telegram_token = os.environ.get("TELEGRAM_TOKEN")
        telegram_bot_available = False
        
        if telegram_token:
            try:
                from src.telegram.telegram_bot import TelegramBotHandler
                
                # Create bot instance
                bot = TelegramBotHandler(telegram_token, orchestrator)
                logger.info("Telegram bot initialized successfully")
                
                # Start bot
                logger.info("Starting Telegram bot with polling")
                telegram_bot_available = True
                bot.start()  # This will block until the bot is stopped
                
            except Exception as e:
                logger.error(f"Failed to start Telegram bot: {str(e)}")
                logger.error(traceback.format_exc())
                from src.utils.error_handler import log_error
                log_error("main", f"Telegram bot error: {str(e)}")
        
        # If Telegram bot failed to start or isn't configured, run in interactive mode
        if not telegram_bot_available:
            logger.info("Running in interactive console mode.")
            print("\n" + "="*50)
            print("   AI Orchestration System - Console Mode")
            print("="*50)
            print("Type your messages below. Type 'exit' to quit.")
            print("="*50 + "\n")
            
            while True:
                try:
                    user_input = input("\nYou: ")
                    if user_input.lower() in ['exit', 'quit', 'bye']:
                        print("\nShutting down AI Orchestration System. Goodbye!")
                        break
                    
                    print("\nProcessing...")
                    response = orchestrator.process_message("console_user", user_input)
                    print("\nAI: " + response)
                except KeyboardInterrupt:
                    print("\n\nKeyboard interrupt detected. Shutting down...")
                    break
                except Exception as e:
                    print(f"\nError processing your request: {str(e)}")
        
    except Exception as e:
        logger.error(f"Failed to start AI Orchestration System: {str(e)}")
        logger.error(traceback.format_exc())
        # Try to log the error if error handler is available
        try:
            from src.utils.error_handler import log_error
            log_error("main", f"Startup error: {str(e)}")
        except Exception as err:
            logger.error(f"Error handler not available. Error: {str(err)}")

if __name__ == "__main__":
    main()
