# fix_google_credentials.py

import os
import sys
import json
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fix_json_credentials():
    """Fix JSON credentials formatting"""
    try:
        # Read the credentials file
        with open("flexmls-scraper-1c4b02856bed.json", "r") as f:
            credentials_data = json.load(f)
        
        # Verify it's valid JSON
        json_string = json.dumps(credentials_data)
        
        # Print first few characters for verification
        logger.info(f"Valid JSON created: {json_string[:30]}...")
        
        # Output the properly formatted JSON string
        print(json_string)
        return True
    except Exception as e:
        logger.error(f"Error processing credentials: {str(e)}")
        return False

if __name__ == "__main__":
    success = fix_json_credentials()
    sys.exit(0 if success else 1)
