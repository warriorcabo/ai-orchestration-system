# telegram_bot.py
import os
import logging
import sys
import re
from typing import Dict, Any, Optional

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext, CallbackQueryHandler

from utils.error_handler import log_error, handle_exception

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("telegram_bot.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class TelegramBotHandler:
    """Handler for Telegram Bot integration"""
    
    def __init__(self, token: str, orchestrator):
        """Initialize the bot with the provided token and orchestrator"""
        self.token = token
        self.orchestrator = orchestrator
        self.pending_full_responses = {}  # Store full responses for users who request them
        
        try:
            # Initialize the updater
            logger.info("Initializing Telegram updater with token")
            self.updater = Updater(token=token)
            self.dispatcher = self.updater.dispatcher
            
            # Register handlers
            self._register_handlers()
            logger.info("Telegram bot handlers registered")
            
        except Exception as e:
            logger.error(f"Failed to initialize Telegram bot: {str(e)}")
            handle_exception("telegram_bot", e)
            raise

    def _register_handlers(self):
        """Register command and message handlers"""
        try:
            # Command handlers
            self.dispatcher.add_handler(CommandHandler("start", self.start_command))
            self.dispatcher.add_handler(CommandHandler("help", self.help_command))
            self.dispatcher.add_handler(CommandHandler("reset", self.reset_command))
            
            # Message handler
            self.dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, self.handle_message))
            
            # Callback query handler for buttons
            self.dispatcher.add_handler(CallbackQueryHandler(self.button_callback))
            
            # Error handler
            self.dispatcher.add_error_handler(self.error_handler)
            
        except Exception as e:
            logger.error(f"Failed to register handlers: {str(e)}")
            handle_exception("telegram_bot", e)
            raise

    def start(self, webhook_url=None):
        """Start the bot using polling or webhooks"""
        try:
            if webhook_url:
                # Use webhook
                logger.info(f"Starting bot with webhook URL: {webhook_url}")
                self.updater.start_webhook(
                    listen="0.0.0.0",
                    port=int(os.environ.get("PORT", 5000)),
                    url_path=self.token,
                    webhook_url=f"{webhook_url}/{self.token}"
                )
                logger.info("Webhook started successfully")
            else:
                # Use polling (simpler for development)
                logger.info("Starting bot with polling")
                self.updater.start_polling()
                logger.info("Polling started successfully")
            
            # Run the bot until Ctrl+C is pressed or process receives SIGINT, SIGTERM, SIGABRT
            logger.info("Bot is running. Press Ctrl+C to stop.")
            self.updater.idle()
            
        except Exception as e:
            logger.error(f"Failed to start bot: {str(e)}")
            handle_exception("telegram_bot", e)
            raise

    def start_command(self, update: Update, context: CallbackContext):
        """Handler for /start command"""
        try:
            user = update.effective_user
            user_id = user.id
            logger.info(f"Received /start command from user {user_id}")
            
            welcome_message = (
                f"Hello {user.first_name}! I'm your AI Orchestration Bot.\n\n"
                f"I can help you work with Gemini and ChatGPT together.\n"
                f"Type a message to get started or use /help to see available commands."
            )
            
            update.message.reply_text(welcome_message)
            logger.info(f"Sent welcome message to user {user_id}")
            
        except Exception as e:
            logger.error(f"Error in start command: {str(e)}")
            handle_exception("telegram_bot", e, user_id=update.effective_user.id if update.effective_user else None)
            update.message.reply_text("Sorry, I encountered an error processing your command.")

    def help_command(self, update: Update, context: CallbackContext):
        """Handler for /help command"""
        try:
            user_id = update.effective_user.id
            logger.info(f"Received /help command from user {user_id}")
            
            help_text = (
                "Here are the available commands:\n\n"
                "/start - Start the bot\n"
                "/help - Show this help message\n"
                "/reset - Reset the current conversation\n\n"
                "Simply type your message to interact with the AI services.\n\n"
                "For lengthy results, I'll provide a summary and ask if you want the full response."
            )
            
            update.message.reply_text(help_text)
            logger.info(f"Sent help message to user {user_id}")
            
        except Exception as e:
            logger.error(f"Error in help command: {str(e)}")
            handle_exception("telegram_bot", e, user_id=update.effective_user.id if update.effective_user else None)
            update.message.reply_text("Sorry, I encountered an error processing your command.")

    def reset_command(self, update: Update, context: CallbackContext):
        """Handler for /reset command to clear conversation history"""
        try:
            user_id = update.effective_user.id
            logger.info(f"Received /reset command from user {user_id}")
            
            # Reset user session in orchestrator
            if hasattr(self.orchestrator, 'user_sessions') and user_id in self.orchestrator.user_sessions:
                self.orchestrator.user_sessions[user_id] = {
                    "history": [],
                    "last_interaction": 0,
                    "feedback_count": 0
                }
                logger.info(f"Reset conversation for user {user_id}")
                update.message.reply_text("Your conversation history has been reset.")
            else:
                logger.info(f"No active session to reset for user {user_id}")
                update.message.reply_text("No active conversation to reset.")
                
        except Exception as e:
            logger.error(f"Error in reset command: {str(e)}")
            handle_exception("telegram_bot", e, user_id=update.effective_user.id if update.effective_user else None)
            update.message.reply_text("Sorry, I encountered an error resetting your conversation.")

    def create_summary(self, full_response: str, max_length: int = 700) -> str:
        """Create a summary of a long response"""
        # If the response is already short, just return it
        if len(full_response) <= max_length:
            return full_response
            
        # Try to extract the first few paragraphs
        paragraphs = full_response.split("\n\n")
        summary = ""
        
        for para in paragraphs:
            if len(summary) + len(para) + 4 <= max_length:  # 4 for the extra newlines
                summary += para + "\n\n"
            else:
                # Add a truncation notice
                remaining_chars = max_length - len(summary) - 30
                if remaining_chars > 20:
                    # Add a partial paragraph
                    summary += para[:remaining_chars] + "...\n\n"
                break
        
        summary += "--- Summary truncated --- "
        return summary

    def handle_message(self, update: Update, context: CallbackContext):
        """Handler for user messages"""
        try:
            user_id = update.effective_user.id
            message_text = update.message.text
            logger.info(f"Received message from user {user_id}: {message_text[:50]}...")
            
            # Inform user that processing is happening
            processing_message = update.message.reply_text("Processing your request... This may take a moment.")
            
            # Pass message to AI Orchestrator
            try:
                logger.info(f"Passing message to AI Orchestrator for user {user_id}")
                full_response = self.orchestrator.process_message(str(user_id), message_text)
                
                # Delete processing message
                context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=processing_message.message_id
                )
                
                # Check if the response is long
                if len(full_response) > 1000:  # Consider longer responses for summary
                    # Create a summary
                    summary = self.create_summary(full_response)
                    
                    # Store the full response for later
                    self.pending_full_responses[str(user_id)] = full_response
                    
                    # Create keyboard buttons
                    keyboard = [
                        [
                            InlineKeyboardButton("Show Full Response", callback_data="show_full_response"),
                            InlineKeyboardButton("This is Enough", callback_data="summary_sufficient")
                        ]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    # Send summary with buttons
                    update.message.reply_text(
                        f"{summary}\n\nWould you like to see the full response?",
                        reply_markup=reply_markup
                    )
                    logger.info(f"Sent summary with options to user {user_id}")
                else:
                    # Send full response directly for shorter responses
                    update.message.reply_text(full_response)
                    logger.info(f"Sent full response to user {user_id} (short response)")
                
                # Try to save to Google Drive if available
                try:
                    if hasattr(self.orchestrator, 'storage'):
                        file_id = self.orchestrator.storage.save_ai_output(
                            full_response, 
                            str(user_id), 
                            "AI Response", 
                            "markdown"
                        )
                        logger.info(f"Saved response to Google Drive with file ID: {file_id}")
                except Exception as e:
                    logger.error(f"Failed to save to Google Drive: {str(e)}")
                    # Don't notify the user about this backend error
                
            except Exception as e:
                logger.error(f"Error in AI Orchestrator: {str(e)}")
                handle_exception("telegram_bot", e, user_id=user_id)
                
                # Delete processing message
                context.bot.delete_message(
                    chat_id=update.effective_chat.id,
                    message_id=processing_message.message_id
                )
                
                # Send error message
                update.message.reply_text(
                    "Sorry, I encountered an error while processing your request.\n"
                    f"Error details: {str(e)}"
                )
                
        except Exception as e:
            logger.error(f"Error handling message: {str(e)}")
            handle_exception("telegram_bot", e, user_id=update.effective_user.id if update.effective_user else None)
            
            # Try to delete processing message if it exists
            try:
                if 'processing_message' in locals():
                    context.bot.delete_message(
                        chat_id=update.effective_chat.id,
                        message_id=processing_message.message_id
                    )
            except:
                pass
                
            update.message.reply_text(
                "Sorry, I encountered an unexpected error. Please try again later."
            )

    def button_callback(self, update: Update, context: CallbackContext):
        """Handle button callbacks"""
        try:
            query = update.callback_query
            user_id = str(query.from_user.id)
            
            # Call the query to stop loading animation
            query.answer()
            
            if query.data == "show_full_response":
                logger.info(f"User {user_id} requested full response")
                
                if user_id in self.pending_full_responses:
                    full_response = self.pending_full_responses[user_id]
                    
                    # Check if the response is too long for Telegram (max 4096 chars)
                    if len(full_response) > 4000:
                        # Split response into chunks
                        chunks = [full_response[i:i+4000] for i in range(0, len(full_response), 4000)]
                        
                        # Send first chunk and edit the current message
                        query.edit_message_text(
                            text=f"(Part 1/{len(chunks)})\n\n{chunks[0]}"
                        )
                        
                        # Send remaining chunks as new messages
                        for i, chunk in enumerate(chunks[1:], start=2):
                            context.bot.send_message(
                                chat_id=update.effective_chat.id,
                                text=f"(Part {i}/{len(chunks)})\n\n{chunk}"
                            )
                        
                        logger.info(f"Sent full response in {len(chunks)} parts to user {user_id}")
                    else:
                        # Response fits in one message
                        query.edit_message_text(text=full_response)
                        logger.info(f"Sent full response to user {user_id}")
                    
                    # Clear from pending responses to free memory
                    del self.pending_full_responses[user_id]
                else:
                    query.edit_message_text(text="Sorry, I couldn't find the full response. It may have expired.")
                    logger.warning(f"Full response not found for user {user_id}")
            
            elif query.data == "summary_sufficient":
                logger.info(f"User {user_id} indicated summary is sufficient")
                
                # Edit message to remove buttons
                query.edit_message_text(
                    text=query.message.text.split("\n\nWould you like to see the full response?")[0] + "\n\n[Summary view]"
                )
                
                # Clear from pending responses to free memory
                if user_id in self.pending_full_responses:
                    del self.pending_full_responses[user_id]
                
        except Exception as e:
            logger.error(f"Error in button callback: {str(e)}")
            handle_exception("telegram_bot", e, user_id=update.callback_query.from_user.id if update.callback_query else None)
            
            try:
                # Notify user of error
                update.callback_query.edit_message_text("Sorry, I encountered an error processing your request.")
            except:
                pass

    def error_handler(self, update: Update, context: CallbackContext):
        """Handle errors in the telegram-python-bot library"""
        try:
            logger.error(f"Update {update} caused telegram error: {context.error}")
            
            user_id = update.effective_user.id if update and update.effective_user else "unknown"
            handle_exception("telegram_bot", context.error, user_id=user_id if user_id != "unknown" else None)
            
            # Try to send a message to the user
            if update and update.effective_chat:
                context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="Sorry, I encountered an error processing your request. Please try again later."
                )
                
        except Exception as e:
            logger.error(f"Error in error handler: {str(e)}")
            # At this point, we can't do much more
