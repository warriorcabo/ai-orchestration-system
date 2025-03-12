from flask import Flask, request, jsonify
import os
import logging
from src.ai_integration.orchestrator import AIOrchestrator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize AI Orchestrator
orchestrator = AIOrchestrator()

@app.route('/')
def index():
    return "AI Orchestration System is running!"

@app.route('/debug')
def debug():
    """Simple debug endpoint to verify the app is running correctly."""
    return jsonify({
        "status": "online",
        "message": "Debug endpoint is working correctly",
        "environment": os.environ.get('FLASK_ENV', 'production')
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
        
        # Return an error response
        return jsonify({
            "status": "error",
            "message": f"Failed to process request: {str(e)}"
        }), 500

if __name__ == "__main__":
    # Get port from environment variable or use default
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
