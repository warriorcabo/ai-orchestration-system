from flask import Flask, request, jsonify
import os
import logging
import time
import threading
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import modules
from src.ai_integration.orchestrator import AIOrchestrator
from src.utils.error_handler import log_error

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize AI Orchestrator
orchestrator = AIOrchestrator()

# Initialize Telegram Bot in a separate thread if token is available
telegram_token = os.environ.get("TELEGRAM_TOKEN", "8183769729:AAEXc0x1BizumecFeTVkEzQ75GjXesTKM24")
webhook_url = os.environ.get("WEBHOOK_URL")

def start_telegram_bot():
    """Start the Telegram bot in a separate thread."""
    try:
        from src.telegram.telegram_bot import TelegramBotHandler
        
        logger.info("Starting Telegram Bot...")
        bot = TelegramBotHandler(telegram_token, orchestrator)
        bot.start(webhook_url)
    except Exception as e:
        logger.error(f"Failed to start Telegram Bot: {str(e)}")
        log_error("telegram_startup", f"Failed to start Telegram Bot: {str(e)}")

# Start Telegram bot in a separate thread if not running in webhook mode
if not webhook_url:
    bot_thread = threading.Thread(target=start_telegram_bot)
    bot_thread.daemon = True
    bot_thread.start()
    logger.info("Telegram Bot thread started")

@app.route('/')
def index():
    return "AI Orchestration System is running!"

@app.route('/debug')
def debug():
    """Simple debug endpoint to verify the app is running correctly."""
    return jsonify({
        "status": "online",
        "message": "Debug endpoint is working correctly",
        "environment": os.environ.get('FLASK_ENV', 'production'),
        "timestamp": time.time()
    })

@app.route('/api/process', methods=['POST'])
def process_request():
    """
    Process incoming requests through the AI Orchestrator.
    
    Expected JSON payload:
    {
        "user_id": "string",
        "message": "string"
    }
    """
    try:
        # Get and validate request data
        data = request.get_json()
        if not data:
            return jsonify({"error": "No JSON payload provided"}), 400
        
        # Validate required fields
        required_fields = ['user_id', 'message']
        for field in required_fields:
            if field not in data:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Log the incoming request
        logger.info(f"Processing request for user: {data['user_id']}")
        
        # Process the request through the orchestrator
        result = orchestrator.process_request(
            user_id=data['user_id'],
            message=data['message']
        )
        
        # Return the result
        return jsonify({
            "status": "success",
            "response": result
        })
        
    except Exception as e:
        # Log the error
        logger.error(f"Error processing request: {str(e)}")
        log_error("api", f"Failed to process request: {str(e)}")
        
        # Return an error response
        return jsonify({
            "status": "error",
            "message": f"Failed to process request: {str(e)}"
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint for monitoring."""
    try:
        # Check components
        components = {
            "app": "healthy",
            "orchestrator": "healthy" if orchestrator else "unavailable"
        }
        
        return jsonify({
            "status": "healthy",
            "components": components,
            "timestamp": time.time()
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            "status": "unhealthy",
            "error": str(e),
            "timestamp": time.time()
        }), 500

@app.route('/webhook/<token>', methods=['POST'])
def telegram_webhook(token):
    """
    Handle incoming webhook requests from Telegram.
    
    Args:
        token: The Telegram bot token as a URL parameter for verification
    """
    if token != telegram_token:
        return jsonify({"error": "Invalid token"}), 403
        
    try:
        from telegram import Update
        from src.telegram.telegram_bot import TelegramBotHandler
        
        # Process the update
        update = Update.de_json(request.get_json(force=True), None)
        
        # Initialize the bot handler on-demand
        bot = TelegramBotHandler(telegram_token, orchestrator)
        
        # Dispatch the update to the appropriate handler
        if update.message:
            if update.message.text.startswith('/'):
                # Command
                command = update.message.text.split()[0].lower()
                if command == '/start':
                    bot.start_command(update, None)
                elif command == '/help':
                    bot.help_command(update, None)
            else:
                # Regular message
                bot.handle_message(update, None)
                
        return jsonify({"status": "ok"})
        
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        log_error("telegram_webhook", f"Error processing webhook: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Run the app
if __name__ == "__main__":
    # Get port from environment variable or use default
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
