# src/ai_integration/connectors/chatgpt_connector.py

import os
import logging
import openai
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
        
        # Get API key from environment variables
        self.api_key = os.environ.get("OPENAI_API_KEY")
        
        # Configure the OpenAI client
        if self.api_key:
            openai.api_key = self.api_key
            self.client = openai.OpenAI(api_key=self.api_key)
        else:
            logger.warning("OpenAI API key not found in environment variables")
            self.client = None
        
        # Default model to use
        self.model = "gpt-4-turbo"
        
        # Default parameters
        self.default_params = {
            "temperature": 0.7,
            "max_tokens": 2048,
            "top_p": 1.0,
            "frequency_penalty": 0,
            "presence_penalty": 0
        }
        
    def execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a structured task using ChatGPT.
        
        Args:
            task: Dictionary containing the structured task information
            
        Returns:
            Dict containing the execution result
        """
        logger.info("Executing task with ChatGPT")
        
        # Check if client is initialized
        if not self.client and not self.api_key:
            logger.warning("ChatGPT client not initialized, using mock response")
            return self._generate_mock_response(task)
            
        try:
            # Extract task information
            task_type = task.get("task_type", "unknown")
            instructions = task.get("instructions", "")
            
            # Create system and user messages
            messages = [
                {"role": "system", "content": self._create_system_prompt(task_type)},
                {"role": "user", "content": self._create_user_prompt(instructions)}
            ]
            
            # Make API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                **self.default_params
            )
            
            # Extract the response content
            content = response.choices[0].message.content if response.choices else "No response generated"
            
            # Create structured response
            return {
                "content": content,
                "model": self.model,
                "completion_tokens": response.usage.completion_tokens if hasattr(response, 'usage') else 0,
                "metadata": {
                    "task_type": task_type,
                    "processing_time_ms": getattr(response, 'response_ms', 0)
                }
            }
            
        except Exception as e:
            logger.error(f"Error executing task with ChatGPT: {str(e)}")
            # Return mock response in case of error
            return self._generate_mock_response(task)
        
    def _create_system_prompt(self, task_type: str) -> str:
        """Create a system prompt based on task type"""
        if task_type == "code_generation":
            return """You are an AI assistant specialized in writing clean, efficient, and well-documented code.
                   Provide detailed explanations of how the code works."""
        elif task_type == "creative":
            return """You are an AI assistant specialized in creative writing and content generation.
                   Be imaginative, engaging, and original in your responses."""
        else:
            return """You are a helpful AI assistant focused on executing tasks accurately and thoroughly.
                   Provide complete, detailed responses that directly address the task at hand."""
    
    def _create_user_prompt(self, instructions: str) -> str:
        """Create a user prompt based on instructions"""
        return f"""
        Please execute the following task carefully and thoroughly:
        
        {instructions}
        
        Provide a comprehensive response that fully addresses all aspects of this request.
        """
        
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
