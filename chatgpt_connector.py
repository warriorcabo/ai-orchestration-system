# chatgpt_connector.py
import os
import json
import logging
from typing import Dict, Any, List, Optional

import openai
from openai import OpenAI

from src.utils.error_handler import log_error

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class ChatGPTConnector:
    """Connector for OpenAI's ChatGPT API"""

    def __init__(self):
        """Initialize the ChatGPT connector with API key"""
        # Get API key from environment variables
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OpenAI API key not found in environment variables")

        # Initialize the OpenAI client
        self.client = OpenAI(api_key=self.api_key)

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

    def generate_response(self, prompt: str, system_message: Optional[str] = None) -> str:
        """Generate a response from ChatGPT based on the prompt"""
        try:
            # Prepare messages
            messages = []

            # Add system message if provided
            if system_message:
                messages.append({"role": "system", "content": system_message})
            else:
                # Default system message
                messages.append({
                    "role": "system",
                    "content": "You are a helpful AI assistant focused on executing tasks accurately and thoroughly."
                })

            # Add user prompt
            messages.append({"role": "user", "content": prompt})

            # Make API call
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                **self.default_params
            )

            # Extract and return the response text
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content

            return "No response generated"

        except openai.RateLimitError as e:
            logger.error(f"OpenAI API rate limit exceeded: {str(e)}")
            log_error("chatgpt_integration", f"Rate limit exceeded: {str(e)}")
            raise

        except openai.APIError as e:
            logger.error(f"OpenAI API error: {str(e)}")
            log_error("chatgpt_integration", f"API error: {str(e)}")
            raise

        except Exception as e:
            logger.error(f"Unexpected error in ChatGPT connector: {str(e)}")
            log_error("chatgpt_integration", f"Unexpected error: {str(e)}")
            raise

    def execute_task(self, task_spec: str, original_query: str) -> str:
        """Execute a specified task based on Gemini's task specification"""
        system_message = self._create_task_execution_system_prompt()
        prompt = self._create_task_execution_prompt(task_spec, original_query)
        return self.generate_response(prompt, system_message)

    def _create_task_execution_system_prompt(self) -> str:
        """Create a system message for task execution"""
        return """
        You are an AI assistant specialized in executing tasks with precision and attention to detail.
        Your responses should be thorough, accurate, and directly address all aspects of the task.
        Focus on providing high-quality, usable outputs following any formatting requirements specified.
        """

    def _create_task_execution_prompt(self, task_spec: str, original_query: str) -> str:
        """Create a prompt for task execution"""
        return f"""
        TASK SPECIFICATION:
        {task_spec}

        ORIGINAL USER QUERY:
        {original_query}

        Please execute this task completely and accurately.
        Make sure to address all requirements and provide a comprehensive response.
        """

    def revise_output(self, original_output: str, feedback: str, original_query: str) -> str:
        """Revise a previous output based on feedback"""
        system_message = self._create_revision_system_prompt()
        prompt = self._create_revision_prompt(original_output, feedback, original_query)
        return self.generate_response(prompt, system_message)

    def _create_revision_system_prompt(self) -> str:
        """Create a system message for output revision"""
        return """
        You are an AI assistant focused on improving your previous responses based on feedback.
        Your task is to analyze the feedback critically and make all necessary changes to produce
        a significantly improved output that addresses all concerns raised.
        """

    def _create_revision_prompt(self, original_output: str, feedback: str, original_query: str) -> str:
        """Create a prompt for revising output"""
        return f"""
        ORIGINAL QUERY:
        {original_query}

        YOUR PREVIOUS RESPONSE:
        {original_output}

        FEEDBACK FOR IMPROVEMENT:
        {feedback}

        Please revise your previous response to address all the feedback points.
        Provide a complete, improved version that fully resolves the issues mentioned.
        """

    def validate_api_key(self) -> bool:
        """Validate that the API key is working properly"""
        try:
            # Simple test query
            response = self.generate_response("Hello, please respond with 'API is working'")
            return "API is working" in response
        except Exception:
            return False

    def estimate_tokens(self, text: str) -> int:
        """Estimate the number of tokens in a text string"""
        # Simple estimation: ~4 characters per token for English text
        return len(text) // 4

    def adjust_parameters_for_task(self, task_type: str) -> Dict[str, Any]:
        """Adjust generation parameters based on task type"""
        params = self.default_params.copy()

        if task_type == "creative":
            params["temperature"] = 0.9
        elif task_type == "technical":
            params["temperature"] = 0.3
        elif task_type == "code":
            params["temperature"] = 0.2

        return params



