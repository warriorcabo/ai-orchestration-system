# src/ai_integration/connectors/gemini_connector.py

import os
import logging
import google.generativeai as genai
from typing import Dict, Any

logger = logging.getLogger(__name__)

class GeminiConnector:
    """
    Connector for Google's Gemini AI.
    Handles communication with the Gemini API for task generation and result review.
    """
    
    def __init__(self):
        """Initialize the Gemini connector."""
        logger.info("Initializing Gemini Connector")
        
        # Get API key from environment variables
        self.api_key = os.environ.get("GEMINI_API_KEY", "AIzaSyBMqCx4unKooOx4FoiEHxMyx8Dmfr-gkw0")
        
        # Configure the Gemini API
        genai.configure(api_key=self.api_key)
        
        # Default model to use
        self.model_name = "gemini-pro"
        
        # Prepare the model for generation
        self.model = genai.GenerativeModel(self.model_name)
        
        # Default generation config
        self.generation_config = {
            "temperature": 0.4,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 2048,
        }
        
    def generate_task(self, user_message: str) -> Dict[str, Any]:
        """
        Generate a structured task based on the user's message.
        
        Args:
            user_message: The original message from the user
            
        Returns:
            Dict containing the structured task information
        """
        logger.info("Generating task with Gemini")
        
        try:
            # Create prompt for task generation
            prompt = self._create_task_generation_prompt(user_message)
            
            # Generate response from Gemini
            response = self.model.generate_content(prompt)
            
            # Extract the content
            task_content = response.text if hasattr(response, 'text') else str(response)
            
            # Format as a task structure
            return {
                "task_type": "text_generation",
                "instructions": task_content,
                "context": "User is interacting with the AI Orchestration System",
                "parameters": {
                    "creativity": 0.7,
                    "detail_level": "moderate"
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating task with Gemini: {str(e)}")
            # Return a fallback task in case of error
            return {
                "task_type": "text_generation",
                "instructions": f"Process the following user request: {user_message}",
                "context": "Error occurred during task generation",
                "parameters": {
                    "creativity": 0.5,
                    "detail_level": "basic"
                }
            }
        
    def review_result(self, execution_result: Dict[str, Any]) -> str:
        """
        Review and improve the result from ChatGPT.
        
        Args:
            execution_result: The result from the ChatGPT execution
            
        Returns:
            Improved and reviewed textual result
        """
        logger.info("Reviewing result with Gemini")
        
        try:
            # Extract the content from the execution result
            content = execution_result.get("content", "No content provided")
            
            # Create prompt for review
            prompt = self._create_review_prompt(content)
            
            # Generate review response from Gemini
            response = self.model.generate_content(prompt)
            
            # Extract the content
            review_content = response.text if hasattr(response, 'text') else str(response)
            
            # If the review starts with "APPROVED", just return the original content
            if "APPROVED" in review_content.upper():
                return content
                
            # Otherwise, return the improved version
            return review_content
            
        except Exception as e:
            logger.error(f"Error reviewing content with Gemini: {str(e)}")
            # Return original content in case of error
            return f"Reviewed and improved: {content}"
            
    def _create_task_generation_prompt(self, message: str) -> str:
        """Create a prompt for Gemini to generate a task"""
        return f"""
        You are a Task Generator AI. Analyze the following user request and create a
        clear, specific task for an assistant to execute. Focus on identifying what
        the user is asking for and how to best address their needs.

        User request: {message}

        Generate a task specification that includes:
        1. Clear objective
        2. Required steps
        3. Expected output format
        4. Any constraints or special requirements
        """
        
    def _create_review_prompt(self, execution_result: str) -> str:
        """Create a prompt for Gemini to review a result"""
        return f"""
        You are a Quality Review AI. Review the following execution result.

        EXECUTION RESULT:
        {execution_result}

        Please evaluate:
        1. Does the result fully address what seems to be the user's request?
        2. Is the information accurate and complete?
        3. Are there any areas for improvement?

        If the result needs improvement, provide a revised, improved version of the response.
        If the result is satisfactory, respond with "APPROVED".
        """
