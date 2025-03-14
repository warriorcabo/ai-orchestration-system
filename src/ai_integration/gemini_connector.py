# gemini_connector.py
import os
import json
import logging
from typing import Dict, Any, List, Optional

import google.generativeai as genai
from google.api_core import exceptions

from src.utils.error_handler import log_error

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class GeminiConnector:
    """Connector for Google's Gemini API"""

    def __init__(self):
        """Initialize the Gemini connector with API key"""
        # Get API key from environment variables
        self.api_key = os.environ.get("GEMINI_API_KEY", "AIzaSyBMqCx4unKooOx4FoiEHxMyx8Dmfr-gkw0")

        # Configure the Gemini API
        # Configure the Gemini API with explicit API key
if not self.api_key:
    logger.error("Gemini API key not found in environment variables")
    raise ValueError("Gemini API key is required. Set GEMINI_API_KEY environment variable.")
    
# Configure with explicit API key
genai.configure(api_key=self.api_key)
logger.info("Gemini API configured with provided API key")

        # Default model to use
        self.model_name = "gemini-1.5-pro"

        # Prepare the model for generation
        # Initialize the model with proper configuration
try:
    self.model = genai.GenerativeModel(self.model_name)
    logger.info(f"Gemini model {self.model_name} initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Gemini model: {str(e)}")
    raise

        # Default generation config
        self.generation_config = {
            "temperature": 0.4,
            "top_p": 0.95,
            "top_k": 40,
            "max_output_tokens": 2048,
        }

        # Safety settings
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]

    def generate_response(self, prompt: str, role: str = "task_generator") -> str:
        """Generate a response from Gemini based on the prompt and role"""
        try:
            # Adjust generation config based on role
            gen_config = self._get_config_for_role(role)

            # Generate the response
            response = self.model.generate_content(
                prompt,
                generation_config=gen_config,
                safety_settings=self.safety_settings
            )

            # Extract and return the text
            if response.candidates and len(response.candidates) > 0:
                if response.candidates[0].content.parts:
                    return response.candidates[0].content.parts[0].text

            # Return empty string if no valid response
            return "No response generated"

        except exceptions.GoogleAPIError as e:
            logger.error(f"Gemini API error: {str(e)}")
            log_error("gemini_integration", f"API error: {str(e)}")
            raise

        except Exception as e:
            logger.error(f"Unexpected error in Gemini connector: {str(e)}")
            log_error("gemini_integration", f"Unexpected error: {str(e)}")
            raise

    def _get_config_for_role(self, role: str) -> Dict[str, Any]:
        """Get the appropriate generation config for the given role"""
        config = self.generation_config.copy()

        if role == "task_generator":
            # Lower temperature for more focused task generation
            config["temperature"] = 0.2

        elif role == "reviewer":
            # Higher temperature for more critical thinking
            config["temperature"] = 0.6

        return config

    def generate_task(self, user_query: str, context: Optional[str] = None) -> str:
        """Generate a task specification based on the user query"""
        prompt = self._create_task_generation_prompt(user_query, context)
        return self.generate_response(prompt, role="task_generator")

    def _create_task_generation_prompt(self, query: str, context: Optional[str] = None) -> str:
        """Create a prompt for task generation"""
        context_text = f"\nAdditional context: {context}" if context else ""

        return f"""
        You are an AI Task Generator specialized in breaking down user requests into clear,
        executable tasks.

        User request: {query}{context_text}

        Create a detailed task specification that includes:
        1. Main objective
        2. Required steps to complete the task
        3. Expected output format
        4. Any special constraints or requirements

        Format your response as a clear, structured task that another AI could execute.
        """

    def review_output(self, original_query: str, ai_output: str) -> str:
        """Review another AI's output for quality and accuracy"""
        prompt = self._create_review_prompt(original_query, ai_output)
        return self.generate_response(prompt, role="reviewer")

    def _create_review_prompt(self, query: str, output: str) -> str:
        """Create a prompt for reviewing AI output"""
        return f"""
        You are an AI Quality Reviewer with expertise in critically analyzing AI-generated content.

        Original user query: {query}

        AI-generated output to review:
        ---
        {output}
        ---

        Please review this output and assess:
        1. Does it fully address the user's query?
        2. Is the information accurate and complete?
        3. Is the response well-structured and clear?
        4. Are there any errors, omissions, or improvements needed?

        If the output is satisfactory in all aspects, respond with just: "APPROVED"

        Otherwise, provide specific, actionable feedback on what should be improved.
        """

    def validate_api_key(self) -> bool:
        """Validate that the API key is working properly"""
        try:
            # Simple test query
            response = self.generate_response("Hello, please respond with 'API is working'")
            return "API is working" in response
        except Exception:
            return False

    def get_token_estimate(self, prompt: str) -> int:
        """Get a rough estimate of tokens in the prompt"""
        # Simple approximation: ~4 characters per token
        return len(prompt) // 4





