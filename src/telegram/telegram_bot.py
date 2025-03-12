# src/telegram/telegram_bot.py

import os
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class TelegramBotHandler:
    """Handler for the Telegram Bot Interface"""
    
    def __init__(self, token, orchestrator):
        """Initialize the Telegram bot with token and AI orchestrator."""
        logger.info("Initializing Telegram Bot Handler")
        self.token = token
        self.orchestrator = orchestrator
        self.updater = Updater(token=token)
        self.dispatcher = self.updater.dispatcher
        
        # Register handlers
        self._register_handlers()
        
    def _register_handlers(self):
        """Register command and message handlers."""
        # Command handlers
        self.dispatcher.add_handler(CommandHandler("start", self.start_command))
        self.dispatcher.add_handler(CommandHandler("help", self.help_command))
        
        # Message handler
        self.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.handle_message))
        
        # Error handler
        self.dispatcher.add_error_handler(self.error_handler)
        
    def start(self, webhook_url=None):
        """Start the bot using polling or webhooks."""
        if webhook_url:
            # Use webhook
            port = int(os.environ.get("PORT", 5000))
            self.updater.start_webhook(
                listen="0.0.0.0",
                port=port,
                url_path=self.token,
                webhook_url=f"{webhook_url}/{self.token}"
            )
            logger.info(f"Started Telegram bot with webhook at {webhook_url}")
        else:
            # Use polling (simpler for development)
            self.updater.start_polling()
            logger.info("Started Telegram bot with polling")
        
        # Run the bot until the process is stopped
        self.updater.idle()
        
    def start_command(self, update: Update, context: CallbackContext):
        """Handler for /start command."""
        user = update.effective_user
        update.message.reply_text(
            f"Hello {user.first_name}! I'm your AI Orchestration Bot. "
            f"I can process your requests using a combination of Gemini and ChatGPT. "
            f"Just send me a message to get started!"
        )
        
    def help_command(self, update: Update, context: CallbackContext):
        """Handler for /help command."""
        update.message.reply_text(
            "Here's how to use this bot:\n\n"
            "• Simply type your question or task, and I'll process it.\n"
            "• I use Gemini and ChatGPT together to generate better responses.\n"
            "• All conversations are stored for future reference.\n\n"
            "Commands:\n"
            "/start - Start or restart the bot\n"
            "/help - Show this help message"
        )
        
    def handle_message(self, update: Update, context: CallbackContext):
        """Handler for incoming messages."""
        user_id = str(update.effective_user.id)
        message_text = update.message.text
        
        try:
            # Send a typing action to show the bot is processing
            context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
            
            # Process message through the AI Orchestrator
            response = self.orchestrator.process_request(user_id, message_text)
            
            # Extract the result from the response
            result = response.get("result", "I couldn't process your request.")
            
            # Send response back to user
            update.message.reply_text(result)
            
            # Log the interaction
            logger.info(f"Processed message from user {user_id}")
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            update.message.reply_text(
                "Sorry, I encountered an error processing your request. "
                "Please try again later."
            )
            
    def error_handler(self, update: Update, context: CallbackContext):
        """Handle errors in the Telegram bot."""
        logger.error(f"Update {update} caused error {context.error}")
        
        # Try to notify user about the error
        if update and update.effective_chat:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Sorry, something went wrong. Please try again later."
            )
