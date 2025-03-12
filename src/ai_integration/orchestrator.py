# src/ai_integration/orchestrator.py

import logging
import time
import uuid
import json
from typing import Dict, Any, Optional

# Import the connectors
from .connectors.gemini_connector import GeminiConnector
from .connectors.chatgpt_connector import ChatGPTConnector

# Import utility modules
from src.utils.error_handler import log_error
from src.utils.feedback_loop_manager import FeedbackLoopManager
from src.utils.google_drive_storage import GoogleDriveStorage

logger = logging.getLogger(__name__)

class AIOrchestrator:
    """
    Central orchestrator that manages communication between different AI services.
    Handles the flow of data between Gemini and ChatGPT, implementing the core logic
    of the AI Orchestration System.
    """
    
    def __init__(self):
        """Initialize the orchestrator with its connectors."""
        logger.info("Initializing AI Orchestrator")
        self.gemini = GeminiConnector()
        self.chatgpt = ChatGPTConnector()
        self.feedback_manager = FeedbackLoopManager()
        self.storage = GoogleDriveStorage()
        
        # User session storage
        self.user_sessions = {}
        
        # Maximum retries for API calls
        self.max_retries = 3
        
    def process_request(self, user_id: str, message: str) -> Dict[str, Any]:
        """
        Process a user request through the appropriate AI services.
        
        Args:
            user_id: Unique identifier for the user
            message: The user's message to process
            
        Returns:
            Dict containing the processed response and any metadata
        """
        logger.info(f"Processing request for user {user_id}")
        
        try:
            # Get or create user session
            session = self.get_or_create_session(user_id)
            
            # Update last interaction time
            session["last_interaction"] = time.time()
            
            # Add user message to history
            session["history"].append({"role": "user", "content": message})
            
            # Generate a conversation ID for this interaction
            conversation_id = f"{user_id}_{uuid.uuid4().hex[:8]}"
            
            # Step 1: Task generation with Gemini
            task_result = self._generate_task(message)
            
            # Step 2: Execute task with ChatGPT
            execution_result = self._execute_task(task_result)
            
            # Extract the content from execution result
            content = execution_result.get("content", "No content provided")
            
            # For simple queries, skip the feedback loop for efficiency
            if len(message.split()) < 5 or "hello" in message.lower():
                final_result = content
                feedback_history = {"revisions": []}
            else:
                # Step 3: Use feedback loop to improve if needed
                final_result, feedback_history = self.feedback_manager.process_feedback_loop(
                    conversation_id=conversation_id,
                    user_query=message,
                    initial_response=content,
                    review_function=self._review_result,
                    revision_function=self._revise_output
                )
            
            # Step 4: Save to storage
            storage_result = self._save_to_storage(message, final_result, user_id, conversation_id)
            
            # Track the process in our records
            self._track_interaction(user_id, message, final_result)
            
            # Add response to history
            session["history"].append({"role": "assistant", "content": final_result})
            
            return {
                "result": final_result,
                "processed_by": "AI Orchestrator",
                "status": "complete",
                "feedback_cycle_count": len(feedback_history.get("revisions", [])),
                "conversation_id": conversation_id,
                "storage_reference": storage_result
            }
            
        except Exception as e:
            logger.error(f"Error in orchestration process: {str(e)}")
            log_error("ai_orchestrator", f"Processing error: {str(e)}")
            # Return a more friendly user-facing error
            return {
                "result": "I encountered an issue processing your request. The team has been notified.",
                "error": str(e),
                "status": "error"
            }
    
    def get_or_create_session(self, user_id: str) -> Dict[str, Any]:
        """Get existing session or create a new one"""
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = {
                "history": [],
                "last_interaction": time.time(),
                "feedback_count": 0
            }
        return self.user_sessions[user_id]
    
    def _generate_task(self, message: str) -> Dict[str, Any]:
        """Generate a structured task from the user message using Gemini."""
        logger.info("Generating task with Gemini")
        for attempt in range(self.max_retries):
            try:
                return self.gemini.generate_task(message)
            except Exception as e:
                logger.warning(f"Gemini API call failed (attempt {attempt+1}): {str(e)}")
                if attempt == self.max_retries - 1:
                    log_error("ai_orchestrator", f"Gemini API call failed: {str(e)}")
                    # Return a fallback task
                    return {
                        "task_type": "text_generation",
                        "instructions": f"Process the following user request: {message}",
                        "context": "Error occurred during task generation",
                        "parameters": {
                            "creativity": 0.5,
                            "detail_level": "basic"
                        }
                    }
                time.sleep(1)  # Wait before retrying
    
    def _execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the structured task using ChatGPT."""
        logger.info("Executing task with ChatGPT")
        for attempt in range(self.max_retries):
            try:
                return self.chatgpt.execute_task(task)
            except Exception as e:
                logger.warning(f"ChatGPT API call failed (attempt {attempt+1}): {str(e)}")
                if attempt == self.max_retries - 1:
                    log_error("ai_orchestrator", f"ChatGPT API call failed: {str(e)}")
                    # Return a fallback response
                    return {
                        "content": f"I processed your request but encountered an issue. Here's what I understand: {task.get('instructions', '')}",
                        "model": "fallback-model",
                        "completion_tokens": 0,
                        "metadata": {
                            "task_type": task.get("task_type", "unknown"),
                            "processing_time_ms": 0
                        }
                    }
                time.sleep(1)  # Wait before retrying
    
    def _review_result(self, response: str, query: str) -> str:
        """Review a response using Gemini."""
        logger.info("Reviewing results with Gemini")
        try:
            # Create a mock execution result to pass to review_result
            mock_execution_result = {"content": response}
            return self.gemini.review_result(mock_execution_result)
        except Exception as e:
            logger.error(f"Error reviewing result: {str(e)}")
            log_error("ai_orchestrator", f"Review error: {str(e)}")
            return "APPROVED"  # Default to approval in case of error
    
    def _revise_output(self, original_output: str, feedback: str, query: str) -> str:
        """Revise output based on feedback."""
        logger.info("Revising output based on feedback")
        try:
            # Create a simplified task for revision to prevent cascading feedback loops
            revision_task = {
                "task_type": "revision",
                "instructions": f"Original query: {query}\n\nFeedback: {feedback}\n\nPlease improve this response."
            }
            
            # Execute the revision task
            result = self.chatgpt.execute_task(revision_task)
            return result.get("content", original_output)
        except Exception as e:
            logger.error(f"Error revising output: {str(e)}")
            log_error("ai_orchestrator", f"Revision error: {str(e)}")
            return original_output  # Return original in case of error
    
    def _save_to_storage(self, query: str, response: str, user_id: str, conversation_id: str) -> str:
        """Save the query and response to storage."""
        logger.info(f"Saving results to storage for conversation {conversation_id}")
        try:
            # Create a structured record
            record = {
                "conversation_id": conversation_id,
                "user_id": user_id,
                "timestamp": time.time(),
                "query": query,
                "response": response
            }
            
            # Convert to JSON
            json_content = json.dumps(record, indent=2)
            
            # Save to Google Drive (with fallback to local storage)
            return self.storage.save_ai_output(
                content=json_content,
                user_id=user_id,
                query_type="conversation",
                format_type="json"
            )
        except Exception as e:
            logger.error(f"Error saving to storage: {str(e)}")
            log_error("ai_orchestrator", f"Storage error: {str(e)}")
            return "storage_error"
    
    def _track_interaction(self, user_id: str, input_message: str, output_result: str) -> None:
        """Track the interaction for feedback loop analysis."""
        logger.info(f"Tracking interaction for user {user_id}")
        # This would connect to your feedback loop manager
        # For now, just log the interaction
        logger.debug(f"User {user_id} - Input: {input_message} - Output length: {len(output_result)} chars")
