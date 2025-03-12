# src/ai_integration/connectors/chatgpt_connector.py

import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

class ChatGPTConnector:
    """
    Connector for OpenAI's ChatGPT.
    Handles communication with the ChatGPT API for task execution.
    """
    
    def __init__(self):
        """Initialize the ChatGPT connector."""
        logger.info("Initializing ChatGPT Connector")
        self.api_key = os.environ.get("OPENAI_API_KEY")
        logger.info(f"API key found: {bool(self.api_key)}")
        self.model = "gpt-4-turbo"
    
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a structured task using ChatGPT.
        
        Args:
            task: Dictionary containing the structured task information
            
        Returns:
            Dict containing the execution result
        """
        logger.info("Executing task with ChatGPT")
        
        try:
            # Try to import and use OpenAI if available
            if self.api_key:
                # Extract task information
                task_type = task.get("task_type", "unknown")
                instructions = task.get("instructions", "")
                
                try:
                    # Try using the OpenAI library
                    from openai import OpenAI
                    client = OpenAI(api_key=self.api_key)
                    
                    # Create messages
                    messages = [
                        {"role": "system", "content": "You are a helpful assistant focused on executing tasks thoroughly."},
                        {"role": "user", "content": instructions}
                    ]
                    
                    # Call the API
                    response = client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        temperature=0.7,
                        max_tokens=2048
                    )
                    
                    # Get the content
                    content = response.choices[0].message.content
                    
                    return {
                        "content": content,
                        "model": self.model,
                        "completion_tokens": 0,
                        "metadata": {
                            "task_type": task_type,
                            "processing_time_ms": 0
                        }
                    }
                    
                except Exception as e:
                    logger.error(f"Error using OpenAI API: {str(e)}")
                    # Fall back to mock response if API call fails
                    return self._generate_mock_response(task)
            else:
                # No API key, use mock response
                return self._generate_mock_response(task)
                
        except Exception as e:
            logger.error(f"Error in ChatGPT connector: {str(e)}")
            # Return mock response in case of error
            return self._generate_mock_response(task)
    
    def _generate_mock_response(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a mock response when API is unavailable"""
        task_type = task.get("task_type", "unknown")
        instructions = task.get("instructions", "")
        
        content = f"This is a mock response to: {instructions}"
        
        return {
            "content": content,
            "model": "gpt-4-mock",
            "completion_tokens": 150,
            "metadata": {
                "task_type": task_type,
                "processing_time_ms": 1200
            }
        }
