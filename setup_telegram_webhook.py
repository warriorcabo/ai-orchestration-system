# setup_telegram_webhook.py

import os
import sys
import logging
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_telegram_webhook():
    """Set up Telegram webhook for production"""
    telegram_token = os.environ.get("TELEGRAM_TOKEN")
    # Use hardcoded URL for now
    app_url = "https://ai-orch-warrior-5ff152a0e1f8.herokuapp.com"
    
    if not telegram_token:
        logger.error("Telegram token not found in environment variables")
        return False
    
    # Format the webhook URL
    webhook_url = f"{app_url}/webhook/{telegram_token}"
    
    # Send request to Telegram API to set webhook
    set_webhook_url = f"https://api.telegram.org/bot{telegram_token}/setWebhook?url={webhook_url}"
    
    try:
        response = requests.get(set_webhook_url)
        response_json = response.json()
        
        if response_json.get("ok"):
            logger.info(f"Webhook set successfully to {webhook_url}")
            logger.info(f"Response: {response_json}")
            return True
        else:
            logger.error(f"Failed to set webhook: {response_json}")
            return False
    except Exception as e:
        logger.error(f"Error setting webhook: {str(e)}")
        return False

if __name__ == "__main__":
    success = setup_telegram_webhook()
    sys.exit(0 if success else 1)
