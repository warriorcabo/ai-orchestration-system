﻿# chatgpt_connector.py
import os
import json
import logging
from typing import Dict, Any, List, Optional

import openai
from openai import OpenAI

from utils.error_handler import log_error

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
        try:
            self.client = OpenAI(api_key=self.api_key)
            logger.info("OpenAI client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            raise

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

            # Make API call with updated OpenAI SDK
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=self.default_params.get("temperature", 0.7),
                max_tokens=self.default_params.get("max_tokens", 2048),
                top_p=self.default_params.get("top_p", 1.0),
                frequency_penalty=self.default_params.get("frequency_penalty", 0),
                presence_penalty=self.default_params.get("presence_penalty", 0)
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
