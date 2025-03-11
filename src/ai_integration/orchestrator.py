# orchestrator.py
import logging
import time
from typing import Dict, Any, List

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class AIOrchestrator:
    """Central orchestrator for managing AI service communication"""

    def __init__(self):
        """Initialize the orchestrator and its connections"""
        # Import modules here to avoid circular imports
        from src.utils.error_handler import log_error
        self.log_error = log_error
        
        # User session storage
        self.user_sessions = {}

        # Maximum retries for API calls
        self.max_retries = 3

        # Maximum feedback loops
        self.max_feedback_loops = 2
        
        # Lazy-load connectors when first needed
        self._gemini = None
        self._chatgpt = None

    @property
    def gemini(self):
        """Lazy-load Gemini connector to avoid initialization issues"""
        if self._gemini is None:
            from src.ai_integration.gemini_connector import GeminiConnector
            self._gemini = GeminiConnector()
        return self._gemini
        
    @property
    def chatgpt(self):
        """Lazy-load ChatGPT connector to avoid initialization issues"""
        if self._chatgpt is None:
            from src.ai_integration.chatgpt_connector import ChatGPTConnector
            self._chatgpt = ChatGPTConnector()
        return self._chatgpt

    def get_or_create_session(self, user_id: str) -> Dict[str, Any]:
        """Get existing session or create a new one"""
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                "history": [],
                "last_interaction": time.time(),
                "feedback_count": 0
            }
        return self.user_sessions[user_id]

    def process_message(self, user_id: str, message: str) -> str:
        """Process an incoming message and determine routing strategy"""
        try:
            # Get or create user session
            session = self.get_or_create_session(user_id)

            # Update last interaction time
            session["last_interaction"] = time.time()

            # Add user message to history
            session["history"].append({"role": "user", "content": message})

            # In a simplified implementation, just use ChatGPT directly
            response = self._call_chatgpt(f"User query: {message}")

            # Add response to history
            session["history"].append({"role": "assistant", "content": response})

            # Return the response
            return response

        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            self.log_error("ai_orchestrator", str(e))
            return "I encountered an error while processing your request. Please try again."

    def _call_gemini(self, prompt: str) -> str:
        """Make a call to Gemini API with retry logic"""
        for attempt in range(self.max_retries):
            try:
                response = self.gemini.generate_response(prompt)
                return response
            except Exception as e:
                logger.warning(f"Gemini API call failed (attempt {attempt+1}): {str(e)}")
                if attempt == self.max_retries - 1:
                    self.log_error("ai_orchestrator", f"Gemini API call failed: {str(e)}")
                    raise
                time.sleep(1)  # Wait before retrying

    def _call_chatgpt(self, prompt: str) -> str:
        """Make a call to ChatGPT API with retry logic"""
        # For testing purposes, just return a mock response
        return f"This is a simulated response to your query: '{prompt}'"
        
        # Uncomment this when ready to use actual API
        '''
        for attempt in range(self.max_retries):
            try:
                response = self.chatgpt.generate_response(prompt)
                return response
            except Exception as e:
                logger.warning(f"ChatGPT API call failed (attempt {attempt+1}): {str(e)}")
                if attempt == self.max_retries - 1:
                    self.log_error("ai_orchestrator", f"ChatGPT API call failed: {str(e)}")
                    raise
                time.sleep(1)  # Wait before retrying
        '''
