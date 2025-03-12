# app.py - Enhanced with debug endpoint and improved logging
import os
import sys
import logging
import json
from flask import Flask, request, jsonify

# Configure detailed logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)]  # Ensure logs go to stdout for Heroku
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

@app.route('/')
def index():
    """Main application page"""
    logger.info("Index page accessed")
    return "AI Orchestration System Dashboard"

@app.route('/debug', methods=['GET'])
def debug_info():
    """Debug endpoint to retrieve environment information"""
    logger.info("Debug endpoint accessed")
    
    # Collect environment information
    debug_data = {
        "environment_variables": {k: v for k, v in os.environ.items() if not k.startswith('_') and k.lower() not in ('api_key', 'secret', 'password', 'token')},
        "python_version": sys.version,
        "working_directory": os.getcwd(),
        "directory_contents": os.listdir(os.getcwd()),
    }
    
    # Log environment info before returning
    logger.info(f"Debug info collected: {json.dumps(debug_data, indent=2)}")
    
    return jsonify(debug_data)

@app.route('/telegram_webhook/<token>', methods=['POST'])
def telegram_webhook(token):
    """Webhook for Telegram bot integration"""
    logger.info(f"Telegram webhook accessed with token: {token[:4]}...")
    
    try:
        update = request.get_json()
        logger.info(f"Received update: {json.dumps(update)}")
        
        # For now, just acknowledge receipt
        return jsonify({"status": "received"})
    
    except Exception as e:
        logger.error(f"Error processing webhook: {str(e)}")
        return jsonify({"status": "error", "message": str(e)}), 500

@app.errorhandler(Exception)
def handle_exception(e):
    """Global exception handler for the Flask app"""
    logger.error(f"Unhandled exception: {str(e)}", exc_info=True)
    return jsonify({"status": "error", "message": "Internal server error"}), 500

if __name__ == "__main__":
    # Get port from environment (required for Heroku)
    port = int(os.environ.get("PORT", 5000))
    
    logger.info(f"Starting AI Orchestration System on port {port}")
    
    # Start Flask app
    app.run(host="0.0.0.0", port=port)
