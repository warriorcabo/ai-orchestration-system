# app.py - Main application entry point
import os
import sys
import logging
import json
from flask import Flask, request, jsonify

# Configure detailed logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Import the AI Orchestrator
try:
    from src.ai_integration.ai_orchestrator import AIOrchestrator
    # Create an instance of the AI Orchestrator
    orchestrator = AIOrchestrator()
    logger.info("AI Orchestrator loaded successfully")
except Exception as e:
    logger.error(f"Failed to load AI Orchestrator: {str(e)}")
    orchestrator = None

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
    
    # Show if orchestrator is initialized
    orchestrator_status = "Initialized" if orchestrator else "Not initialized"
    
    # Collect environment information
    debug_data = {
        "ENV": os.environ.get('DYNO', 'No dyno'),
        "ORCHESTRATOR": orchestrator_status
    }
    
    return jsonify(debug_data)

@app.route('/api/process', methods=['POST'])
def process_message():
    """Process a message through the AI Orchestrator"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        user_id = data.get('user_id', 'anonymous')
        message = data.get('message')
        
        if not message:
            return jsonify({"error": "No message provided"}), 400
            
        if not orchestrator:
            return jsonify({"error": "AI Orchestrator not initialized"}), 500
            
        # Process the message through the orchestrator
        response = orchestrator.process_message(user_id, message)
        
        return jsonify({
            "user_id": user_id,
            "response": response
        })
        
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        return jsonify({"error": str(e)}), 500

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
