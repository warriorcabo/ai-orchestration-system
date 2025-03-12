import os
import sys
import logging
import traceback
from flask import Flask, jsonify

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Simple error handler
def log_error(module, message, exception=None):
    """Simple error logging function"""
    error_info = {
        "module": module,
        "message": message,
        "traceback": traceback.format_exc() if exception else None
    }
    
    logger.error(f"{module} - {message}")
    return error_info

@app.route('/')
def index():
    """Main dashboard page"""
    try:
        logger.info("Accessing main dashboard page")
        return 'AI Orchestration System Dashboard'
    except Exception as e:
        log_error("dashboard", f"Error displaying dashboard: {str(e)}", e)
        return f"An error occurred: {str(e)}", 500

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({"status": "ok"})

@app.route('/webhook', methods=['POST', 'GET'])
def webhook():
    """Webhook endpoint for Telegram"""
    try:
        logger.info("Webhook accessed")
        return 'Webhook endpoint ready'
    except Exception as e:
        log_error("webhook", f"Error in webhook: {str(e)}", e)
        return f"An error occurred: {str(e)}", 500

@app.errorhandler(404)
def page_not_found(e):
    """Handle 404 errors"""
    return "Page not found", 404

@app.errorhandler(500)
def server_error(e):
    """Handle 500 errors"""
    log_error("server", f"Server error: {str(e)}", e)
    return "Internal server error", 500

if __name__ == '__main__':
    try:
        port = int(os.environ.get('PORT', 5000))
        app.run(host='0.0.0.0', port=port)
    except Exception as e:
        log_error("startup", f"Failed to start application: {str(e)}", e)
        sys.exit(1)
