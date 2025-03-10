# Update Telegram bot to include more logging
import os
import logging
import traceback
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Configure detailed logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG  # Changed to DEBUG for more details
)
logger = logging.getLogger(__name__)

class TelegramBotHandler:
    """Handler for Telegram bot interactions"""
    
    def __init__(self, token, orchestrator):
        """Initialize the bot with the provided token and orchestrator"""
        logger.debug(f"Initializing TelegramBotHandler with token: {token[:5]}...")
        self.token = token
        self.orchestrator = orchestrator
        self.updater = Updater(token=token)
        self.dispatcher = self.updater.dispatcher
        
        # Register handlers
        self._register_handlers()
        
        logger.info("Telegram bot initialized successfully")
    
    def _register_handlers(self):
        """Register command and message handlers"""
        # Command handlers
        logger.debug("Registering command handlers...")
        self.dispatcher.add_handler(CommandHandler("start", self.start_command))
        self.dispatcher.add_handler(CommandHandler("help", self.help_command))
        
        # Message handler
        logger.debug("Registering message handlers...")
        self.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.handle_message))
        
        # Error handler
        self.dispatcher.add_error_handler(self.error_handler)
        
        logger.debug("All handlers registered successfully")
    
    def start_command(self, update: Update, context: CallbackContext):
        """Handler for /start command"""
        user = update.effective_user
        logger.info(f"Start command received from user: {user.id} ({user.first_name})")
        update.message.reply_text(
            f"Hello {user.first_name}! I'm your AI Orchestration Bot. "
            f"I can help you work with Gemini and ChatGPT. "
            f"Type a message to get started or use /help to see available commands."
        )
    
    def help_command(self, update: Update, context: CallbackContext):
        """Handler for /help command"""
        user = update.effective_user
        logger.info(f"Help command received from user: {user.id}")
        help_text = (
            "Here are the available commands:\n\n"
            "/start - Start the bot\n"
            "/help - Show this help message\n\n"
            "Simply type your message to interact with the AI services."
        )
        update.message.reply_text(help_text)
    
    def handle_message(self, update: Update, context: CallbackContext):
        """Handler for user messages"""
        user_id = update.effective_user.id
        message_text = update.message.text
        logger.info(f"Message received from user {user_id}: {message_text[:20]}...")
        
        try:
            # Inform user that processing is happening
            processing_message = update.message.reply_text("Processing your request...")
            
            # Pass message to AI Orchestrator
            logger.debug(f"Passing message to orchestrator: {message_text[:30]}...")
            response = self.orchestrator.process_message(str(user_id), message_text)
            logger.debug(f"Received response from orchestrator: {response[:30]}...")
            
            # Send response back to user
            update.message.reply_text(response)
            logger.info(f"Response sent to user {user_id}")
            
            # Delete the processing message
            try:
                context.bot.delete_message(
                    chat_id=processing_message.chat_id,
                    message_id=processing_message.message_id
                )
            except Exception as e:
                logger.warning(f"Could not delete processing message: {str(e)}")
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            logger.error(traceback.format_exc())
            update.message.reply_text(
                "Sorry, I encountered an error while processing your request. "
                "Please try again later."
            )
            
            # Log the error with our error handling system
            from src.utils.error_handler import log_error
            log_error("telegram_bot", f"Message processing error: {str(e)}")
    
    def error_handler(self, update: Update, context: CallbackContext):
        """Handle errors in the telegram-python-bot library"""
        logger.error(f"Update {update} caused error {context.error}")
        logger.error(traceback.format_exc())
        
        # Log the error with our error handling system
        from src.utils.error_handler import log_error
        log_error("telegram_bot", f"Telegram library error: {str(context.error)}")
    
    def start(self, webhook_url=None):
        """Start the bot using polling or webhooks"""
        if webhook_url:
            # Use webhook
            logger.info(f"Starting bot with webhook URL: {webhook_url}")
            port = int(os.environ.get("PORT", 5000))
            self.updater.start_webhook(
                listen="0.0.0.0",
                port=port,
                url_path=self.token,
                webhook_url=f"{webhook_url}/{self.token}"
            )
            logger.info(f"Telegram bot started with webhook at {webhook_url} on port {port}")
        else:
            # Use polling (simpler for development)
            logger.info("Starting bot with polling")
            self.updater.start_polling()
            logger.info("Telegram bot started with polling")
        
        # Run the bot until the user presses Ctrl-C
        self.updater.idle()
