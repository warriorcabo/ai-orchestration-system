﻿# Fix for ChatGPT connector execute_task method
import os
import logging
import openai

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ChatGPTConnector:
    """Connector for OpenAI's ChatGPT API"""

    def __init__(self):
        """Initialize the ChatGPT connector with API key"""
        # Get API key from environment variables
        self.api_key = os.environ.get("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("OpenAI API key not found in environment variables")
            self.is_available = False
            return
            
        # Set API key
        openai.api_key = self.api_key
        
        # Default model to use
        self.model = "gpt-4-0125-preview"
        
        # Default parameters
        self.default_params = {
            "temperature": 0.7,
            "max_tokens": 2048,
            "top_p": 1.0,
            "frequency_penalty": 0,
            "presence_penalty": 0
        }
        
        self.is_available = True
        logger.info("ChatGPT connector initialized successfully")

    def generate_response(self, prompt, system_message=None):
        """Generate a response from ChatGPT based on the prompt"""
        try:
            if not self.is_available:
                return "ChatGPT API not available"
                
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
            
            # Make API call - remove proxies parameter if it exists
            safe_params = {k: v for k, v in self.default_params.items() if k != 'proxies'}
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                **safe_params
            )
            
            # Extract and return the response text
            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content
                
            return "No response generated by ChatGPT"
            
        except Exception as e:
            logger.error(f"Error using OpenAI API: {str(e)}")
            return f"ChatGPT Error: {str(e)}"
            
    def execute_task(self, task_spec, original_query=None):
        """Execute a specified task based on task specification"""
        if original_query is None:
            original_query = "Unknown query"
            
        try:
            system_message = """
            You are an AI assistant specialized in executing tasks with precision and attention to detail.
            Your responses should be thorough, accurate, and directly address all aspects of the task.
            Focus on providing high-quality, usable outputs following any formatting requirements specified.
            """
            
            prompt = f"""
            TASK SPECIFICATION:
            {task_spec}
            
            ORIGINAL USER QUERY:
            {original_query}
            
            Please execute this task completely and accurately.
            Make sure to address all requirements and provide a comprehensive response.
            """
            
            return self.generate_response(prompt, system_message)
        except Exception as e:
            logger.error(f"Error executing task with ChatGPT: {str(e)}")
            return f"Task Execution Error: {str(e)}"
