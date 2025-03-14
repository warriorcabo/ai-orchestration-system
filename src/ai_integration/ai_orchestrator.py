# ai_orchestrator.py
import logging
import json
import time
import os
from typing import Dict, Any, List, Optional

# Import AI connectors
from src.ai_integration.gemini_connector import GeminiConnector
from src.ai_integration.chatgpt_connector import ChatGPTConnector
from src.storage.google_drive_storage import GoogleDriveStorage
from utils.error_handler import log_error

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
        try:
            # Initialize AI service connectors
            logger.info("Initializing Gemini connector...")
            self.gemini = GeminiConnector()
            
            logger.info("Initializing ChatGPT connector...")
            self.chatgpt = ChatGPTConnector()
            
            logger.info("Initializing Google Drive storage...")
            self.storage = GoogleDriveStorage()

            # User session storage
            self.user_sessions: Dict[str, Dict[str, Any]] = {}

            # Maximum retries for API calls
            self.max_retries = int(os.environ.get("MAX_API_RETRIES", "3"))

            # Maximum feedback loops
            self.max_feedback_loops = int(os.environ.get("MAX_FEEDBACK_LOOPS", "2"))
            
            logger.info("AI Orchestrator initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing AI Orchestrator: {str(e)}")
            log_error("ai_orchestrator", f"Initialization error: {str(e)}")
            raise

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

            logger.info(f"Processing message from user {user_id}: {message[:50]}...")

            # Step 1: Generate task with Gemini
            try:
                logger.info("Generating task with Gemini...")
                task_prompt = self._create_task_prompt(message, session["history"])
                task_response = self._call_gemini(task_prompt)
                logger.info(f"Task generated successfully: {task_response[:50]}...")
            except Exception as e:
                logger.error(f"Error generating task with Gemini: {str(e)}")
                log_error("ai_orchestrator", f"Gemini task generation error: {str(e)}")
                # Don't use mock responses - return a helpful error message
                return f"I encountered an issue connecting to our AI services. Please try again in a few moments. Error details: {str(e)}"

            # Step 2: Execute with ChatGPT
            try:
                logger.info("Executing task with ChatGPT...")
                execution_prompt = self._create_execution_prompt(task_response, message)
                execution_response = self._call_chatgpt(execution_prompt)
                logger.info(f"Task executed successfully: {execution_response[:50]}...")
            except Exception as e:
                logger.error(f"Error executing task with ChatGPT: {str(e)}")
                log_error("ai_orchestrator", f"ChatGPT execution error: {str(e)}")
                # Don't use mock responses - return the task generation at least
                return f"I've analyzed your request and created a plan, but I'm having trouble executing it at the moment. Here's my analysis: \n\n{task_response}\n\nPlease try again in a few moments."

            # Step 3: Review with Gemini if needed
            final_response = execution_response
            try:
                if self._needs_review(execution_response):
                    if session["feedback_count"] < self.max_feedback_loops:
                        session["feedback_count"] += 1
                        logger.info("Reviewing execution results with Gemini...")
                        review_prompt = self._create_review_prompt(execution_response, message)
                        review_response = self._call_gemini(review_prompt)
                        logger.info(f"Review completed: {review_response[:50]}...")

                        # If review suggests changes, send back to ChatGPT
                        if self._suggests_changes(review_response):
                            logger.info("Review suggests changes, sending for revision...")
                            revision_prompt = self._create_revision_prompt(
                                execution_response, review_response, message
                            )
                            final_response = self._call_chatgpt(revision_prompt)
                            logger.info(f"Revision completed: {final_response[:50]}...")
            except Exception as e:
                logger.error(f"Error in feedback loop: {str(e)}")
                log_error("ai_orchestrator", f"Feedback loop error: {str(e)}")
                # Use the execution_response as a fallback
                final_response = execution_response

            # Reset feedback count for next request
            session["feedback_count"] = 0

            # Add final response to history
            session["history"].append({"role": "assistant", "content": final_response})

            # Try to save the response to Google Drive
            try:
                logger.info("Saving response to Google Drive...")
                file_id = self.storage.save_ai_output(
                    final_response, 
                    user_id, 
                    "AI Response", 
                    "markdown"
                )
                logger.info(f"Response saved with file ID: {file_id}")
            except Exception as e:
                logger.error(f"Error saving to Google Drive: {str(e)}")
                log_error("ai_orchestrator", f"Google Drive storage error: {str(e)}")
                # Continue without storage - don't fail the whole request

            # Return the final response
            return final_response

        except Exception as e:
            logger.error(f"Unexpected error processing message: {str(e)}")
            log_error("ai_orchestrator", str(e), user_id=user_id)
            return f"I encountered an unexpected error while processing your request. Technical details: {str(e)}"

    def _call_gemini(self, prompt: str) -> str:
        """Make a call to Gemini API with retry logic"""
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Calling Gemini API (attempt {attempt+1})...")
                response = self.gemini.generate_response(prompt)
                return response
            except Exception as e:
                logger.warning(f"Gemini API call failed (attempt {attempt+1}): {str(e)}")
                if attempt == self.max_retries - 1:
                    log_error("ai_orchestrator", f"Gemini API call failed: {str(e)}")
                    raise
                time.sleep(1)  # Wait before retrying

    def _call_chatgpt(self, prompt: str) -> str:
        """Make a call to ChatGPT API with retry logic"""
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Calling ChatGPT API (attempt {attempt+1})...")
                response = self.chatgpt.generate_response(prompt)
                return response
            except Exception as e:
                logger.warning(f"ChatGPT API call failed (attempt {attempt+1}): {str(e)}")
                if attempt == self.max_retries - 1:
                    log_error("ai_orchestrator", f"ChatGPT API call failed: {str(e)}")
                    raise
                time.sleep(1)  # Wait before retrying

    def _create_task_prompt(self, message: str, history: List[Dict[str, str]]) -> str:
        """Create a prompt for Gemini to generate a task"""
        return f"""
        You are a Task Generator AI. Analyze the following user request and create a
        clear, specific task for an assistant to execute. Focus on identifying what
        the user is asking for and how to best address their needs.

        User history: {self._format_history(history)}

        Current user request: {message}

        Generate a task specification that includes:
        1. Clear objective
        2. Required steps
        3. Expected output format
        4. Any constraints or special requirements
        """

    def _create_execution_prompt(self, task: str, original_message: str) -> str:
        """Create a prompt for ChatGPT to execute the task"""
        return f"""
        You are an AI Assistant focused on executing tasks. Please complete the following task:

        TASK SPECIFICATION:
        {task}

        ORIGINAL USER REQUEST:
        {original_message}

        Execute this task step by step, providing a detailed and accurate response.
        """

    def _create_review_prompt(self, execution_result: str, original_message: str) -> str:
        """Create a prompt for Gemini to review ChatGPT's execution"""
        return f"""
        You are a Quality Review AI. Review the following execution result for the given user request.

        ORIGINAL USER REQUEST:
        {original_message}

        EXECUTION RESULT:
        {execution_result}

        Please evaluate:
        1. Does the result fully address the user's request?
        2. Is the information accurate and complete?
        3. Are there any areas for improvement?

        Provide specific feedback on what needs to be changed, if anything.
        If the result is satisfactory, respond with "APPROVED".
        """

    def _create_revision_prompt(self, execution_result: str, review_feedback: str, original_message: str) -> str:
        """Create a prompt for ChatGPT to revise based on feedback"""
        return f"""
        You are an AI Assistant revising a previous response based on feedback.

        ORIGINAL USER REQUEST:
        {original_message}

        YOUR PREVIOUS RESPONSE:
        {execution_result}

        FEEDBACK FOR IMPROVEMENT:
        {review_feedback}

        Please revise your previous response addressing all the points in the feedback.
        Provide a complete, improved response.
        """

    def _format_history(self, history: List[Dict[str, str]]) -> str:
        """Format conversation history for inclusion in prompts"""
        if not history:
            return "No previous conversation"

        formatted = []
        for entry in history[-5:]:  # Only include last 5 exchanges to save tokens
            role = "User" if entry["role"] == "user" else "Assistant"
            formatted.append(f"{role}: {entry['content']}")

        return "\n".join(formatted)

    def _needs_review(self, response: str) -> bool:
        """Determine if a response needs review"""
        # For initial implementation, review all responses
        # In a more advanced implementation, we could use
        # heuristics or ML to determine which responses need review
        return True

    def _suggests_changes(self, review_response: str) -> bool:
        """Check if the review suggests changes"""
        # Simple implementation - if response contains "APPROVED", no changes needed
        return "APPROVED" not in review_response.upper()
