# src/ai_integration/orchestrator.py

import logging
from typing import Dict, Any, Optional

# Import the connectors (mock implementations for now)
from .connectors.gemini_connector import GeminiConnector
from .connectors.chatgpt_connector import ChatGPTConnector

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
            # Step 1: Task generation with Gemini
            task_result = self._generate_task(message)
            
            # Step 2: Execute task with ChatGPT
            execution_result = self._execute_task(task_result)
            
            # Step 3: Review and improve with Gemini
            final_result = self._review_result(execution_result)
            
            # Track the process in our records
            self._track_interaction(user_id, message, final_result)
            
            return {
                "result": final_result,
                "processed_by": "AI Orchestrator",
                "status": "complete"
            }
            
        except Exception as e:
            logger.error(f"Error in orchestration process: {str(e)}")
            # Return a more friendly user-facing error
            return {
                "result": "I encountered an issue processing your request. The team has been notified.",
                "error": str(e),
                "status": "error"
            }
    
    def _generate_task(self, message: str) -> Dict[str, Any]:
        """Generate a structured task from the user message using Gemini."""
        logger.info("Generating task with Gemini")
        return self.gemini.generate_task(message)
    
    def _execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the structured task using ChatGPT."""
        logger.info("Executing task with ChatGPT")
        return self.chatgpt.execute_task(task)
    
    def _review_result(self, execution_result: Dict[str, Any]) -> str:
        """Review and improve the execution result using Gemini."""
        logger.info("Reviewing results with Gemini")
        return self.gemini.review_result(execution_result)
    
    def _track_interaction(self, user_id: str, input_message: str, output_result: str) -> None:
        """Track the interaction for feedback loop analysis."""
        logger.info(f"Tracking interaction for user {user_id}")
        # This would connect to your feedback loop manager
        # For now, just log the interaction
        logger.debug(f"User {user_id} - Input: {input_message} - Output: {output_result}")
