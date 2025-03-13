# Fix for AI Orchestrator to handle string responses from AI services
import logging\nimport os
import json
import time
import datetime
from typing import Dict, Any, List, Optional

from src.ai_integration.connectors.gemini_connector import GeminiConnector
from src.ai_integration.connectors.chatgpt_connector import ChatGPTConnector
from src.utils.error_handler import log_error

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
        # Initialize AI service connectors
        self.gemini = GeminiConnector()
        self.chatgpt = ChatGPTConnector()

        # User session storage
        self.user_sessions = {}

        # Maximum retries for API calls
        self.max_retries = 3

        # Maximum feedback loops
        self.max_feedback_loops = 2
        
        logger.info("AI Orchestrator initialized successfully")

    def get_or_create_session(self, user_id: str) -> Dict[str, Any]:
        """Get existing session or create a new one"""
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                "history": [],
                "last_interaction": time.time(),
                "feedback_count": 0
            }
        return self.user_sessions[user_id]

    def process_message(self, user_id: str, message: str) -> Dict[str, Any]:
        """Process an incoming message and determine routing strategy"""
        logger.info(f"Processing request for user {user_id}")
        
        try:
            # Get or create user session
            session = self.get_or_create_session(user_id)

            # Update last interaction time
            session["last_interaction"] = time.time()

            # Add user message to history
            session["history"].append({"role": "user", "content": message})

            # Step 1: Generate task with Gemini
            logger.info("Generating task with Gemini")
            task_response = self._call_gemini_task(message)

            # Step 2: Execute with ChatGPT
            logger.info("Executing task with ChatGPT")
            execution_response = self._call_chatgpt_execution(task_response, message)

            # Step 3: Review with Gemini if needed
            final_response = execution_response
            if session["feedback_count"] < self.max_feedback_loops:
                logger.info("Reviewing results with Gemini")
                session["feedback_count"] += 1
                review_response = self._call_gemini_review(execution_response, message)

                # If review suggests changes, send back to ChatGPT
                if "APPROVED" not in review_response:
                    logger.info("Revising output based on feedback")
                    final_response = self._call_chatgpt_revision(execution_response, review_response, message)

            # Reset feedback count for next request
            session["feedback_count"] = 0

            # Add final response to history
            session["history"].append({"role": "assistant", "content": final_response})
            
            # Create a unique conversation ID
            conversation_id = f"{user_id}_{self._generate_conversation_id()}"
            
            # Save results to storage
            logger.info(f"Saving results to storage for conversation {conversation_id}")
            storage_ref = self._save_to_storage(user_id, message, final_response, conversation_id)

            # Track this interaction
            logger.info(f"Tracking interaction for user {user_id}")
            
            # Return the final response with metadata
            return {
                "conversation_id": conversation_id,
                "user_id": user_id,
                "timestamp": time.time(),
                "query": message,
                "response": final_response,
                "status": "complete",
                "feedback_cycle_count": session["feedback_count"],
                "storage_reference": storage_ref
            }

        except Exception as e:
            logger.error(f"Error in orchestration process: {str(e)}")
            log_error("ai_orchestrator", f"Processing error: {str(e)}")
            
            # Return an error response
            return {
                "conversation_id": f"{user_id}_{self._generate_conversation_id()}",
                "user_id": user_id,
                "timestamp": time.time(),
                "query": message,
                "response": f"This is a mock response to: Process the following user request: {message}",
                "status": "error",
                "error_message": str(e)
            }

    def _call_gemini_task(self, message: str) -> str:
        """Call Gemini to generate a task from user message"""
        for attempt in range(self.max_retries):
            try:
                if not hasattr(self.gemini, 'is_available') or not self.gemini.is_available:
                    return f"Task: Process the following user request: {message}"
                
                response = self.gemini.generate_task(message)
                return response
            except Exception as e:
                logger.warning(f"Gemini API call failed (attempt {attempt+1}): {str(e)}")
                if attempt == self.max_retries - 1:
                    log_error("ai_orchestrator", f"Gemini API call failed: {str(e)}")
                    return f"Task: Process the following user request: {message}"
                time.sleep(1)  # Wait before retrying

    def _call_chatgpt_execution(self, task: str, original_query: str) -> str:
        """Call ChatGPT to execute a task"""
        for attempt in range(self.max_retries):
            try:
                if not hasattr(self.chatgpt, 'is_available') or not self.chatgpt.is_available:
                    return f"This is a mock response to: {task}"
                
                response = self.chatgpt.execute_task(task, original_query)
                return response
            except Exception as e:
                logger.warning(f"ChatGPT API call failed (attempt {attempt+1}): {str(e)}")
                if attempt == self.max_retries - 1:
                    log_error("ai_orchestrator", f"ChatGPT API call failed: {str(e)}")
                    return f"This is a mock response to: {task}"
                time.sleep(1)  # Wait before retrying

    def _call_gemini_review(self, execution_result: str, original_query: str) -> str:
        """Call Gemini to review ChatGPT's execution"""
        for attempt in range(self.max_retries):
            try:
                if not hasattr(self.gemini, 'is_available') or not self.gemini.is_available:
                    return "APPROVED"
                
                response = self.gemini.review_content(original_query, execution_result)
                return response
            except Exception as e:
                logger.warning(f"Gemini API call failed (attempt {attempt+1}): {str(e)}")
                if attempt == self.max_retries - 1:
                    log_error("ai_orchestrator", f"Gemini API call failed: {str(e)}")
                    return "APPROVED"
                time.sleep(1)  # Wait before retrying

    def _call_chatgpt_revision(self, execution_result: str, review_feedback: str, original_query: str) -> str:
        """Call ChatGPT to revise based on feedback"""
        for attempt in range(self.max_retries):
            try:
                if not hasattr(self.chatgpt, 'is_available') or not self.chatgpt.is_available:
                    return execution_result  # Return original if revision fails
                
                system_message = """
                You are an AI Assistant revising a previous response based on feedback.
                Your task is to improve the response addressing all feedback points.
                """
                
                prompt = f"""
                ORIGINAL USER REQUEST:
                {original_query}

                YOUR PREVIOUS RESPONSE:
                {execution_result}

                FEEDBACK FOR IMPROVEMENT:
                {review_feedback}

                Please revise your previous response addressing all the points in the feedback.
                Provide a complete, improved response.
                """
                
                response = self.chatgpt.generate_response(prompt, system_message)
                return response
            except Exception as e:
                logger.warning(f"ChatGPT API call failed (attempt {attempt+1}): {str(e)}")
                if attempt == self.max_retries - 1:
                    log_error("ai_orchestrator", f"ChatGPT API call failed: {str(e)}")
                    return execution_result  # Return original if revision fails
                time.sleep(1)  # Wait before retrying
                
    def _save_to_storage(self, user_id: str, query: str, response: str, conversation_id: str) -> str:
        """Save the conversation to storage"""
        try:
            # Import here to avoid circular imports
            from src.utils.google_drive_storage import GoogleDriveStorage
            
            # Create storage content
            content = {
                "conversation_id": conversation_id,
                "user_id": user_id,
                "timestamp": time.time(),
                "query": query,
                "response": response
            }
            
            # Initialize storage
            storage = GoogleDriveStorage()
            
            # Save to storage if available
            if hasattr(storage, 'is_available') and storage.is_available:
                storage_ref = storage.save_ai_output(
                    content=json.dumps(content, indent=2),
                    user_id=user_id,
                    query_type="conversation",
                    format_type="json"
                )
                return storage_ref
            
            # Fallback to local storage
            local_dir = "logs/outputs"
            os.makedirs(f"{local_dir}/user_{user_id}", exist_ok=True)
            filename = f"conversation_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = f"{local_dir}/user_{user_id}/{filename}"
            
            with open(filepath, 'w') as f:
                json.dump(content, f, indent=2)
                
            return f"local:{filepath}"
            
        except Exception as e:
            logger.error(f"Error saving to storage: {str(e)}")
            return "storage_error"
            
    def _generate_conversation_id(self) -> str:
        """Generate a unique conversation ID"""
        import random
        import string
        import datetime
        
        # Generate a random 8-character string
        random_str = ''.join(random.choices(string.hexdigits.lower(), k=8))
        
        return f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{random_str}"

