# app.py
import os
import logging
import json
from flask import Flask, request, jsonify
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Import components
from src.ai_integration.orchestrator import AIOrchestrator
from src.utils.error_handler import log_error

# Initialize Flask app
app = Flask(__name__)

# Initialize AI Orchestrator
orchestrator = AIOrchestrator()

@app.route('/api/process', methods=['POST'])
def process_message():
    """Process a message from the user"""
    try:
        # Get request data
        data = request.json
        
        # Extract user_id and message
        user_id = data.get('user_id', 'anonymous_user')
        message = data.get('message', '')
        
        logger.info(f"Processing request for user: {user_id}")
        
        # Process the message with the orchestrator
        result = orchestrator.process_message(user_id, message)
        
        # Return the result
        return jsonify({
            "status": "success",
            "response": result
        })
    except Exception as e:
        logger.error(f"Failed to process request: {str(e)}")
        log_error("app", f"Request processing error: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Failed to process request: {str(e)}"
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "services": {
            "orchestrator": hasattr(orchestrator, 'process_message'),
            "gemini": hasattr(orchestrator, 'gemini') and hasattr(orchestrator.gemini, 'is_available'),
            "chatgpt": hasattr(orchestrator, 'chatgpt') and hasattr(orchestrator.chatgpt, 'is_available')
        }
    })

if __name__ == '__main__':
    # Get port from environment variable
    port = int(os.environ.get("PORT", 5000))
    
    # Start the Flask app
    app.run(host="0.0.0.0", port=port)
