from flask import Flask, request, jsonify
import os
import logging
import time
import json
from src.ai_integration.orchestrator import AIOrchestrator
from src.utils.error_handler import log_error

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

@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get basic system statistics."""
    try:
        stats = {
            "active_users": len(orchestrator.user_sessions) if hasattr(orchestrator, 'user_sessions') else 0,
            "uptime": time.time() - app.start_time if hasattr(app, 'start_time') else 0,
            "api_calls": {
                "process_requests": app.request_count if hasattr(app, 'request_count') else 0
            }
        }
        
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Failed to get stats: {str(e)}")
        return jsonify({"error": str(e)}), 500

# Track application start time and request count
@app.before_first_request
def before_first_request():
    """Initialize counters before first request."""
    app.start_time = time.time()
    app.request_count = 0

@app.before_request
def before_request():
    """Increment request counter before each request."""
    if request.endpoint == 'process_request':
        app.request_count = getattr(app, 'request_count', 0) + 1

# Add environment variable handling
if __name__ == "__main__":
    # Get port from environment variable or use default
    port = int(os.environ.get("PORT", 5000))
    
    # Set start time
    app.start_time = time.time()
    app.request_count = 0
    
    # Start the Flask app
    app.run(host="0.0.0.0", port=port)
