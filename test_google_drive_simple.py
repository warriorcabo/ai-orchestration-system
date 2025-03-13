# test_google_drive.py

import os
import sys
import logging
import json
import datetime
import io
import tempfile
from dotenv import load_dotenv

# Add the project root to sys.path for imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Create a simple test that doesn't rely on imports
def test_google_drive_credentials():
    """Test if Google Drive credentials are available"""
    logger.info("Testing Google Drive credentials...")
    
    # Check environment variables
    folder_id = os.environ.get("GOOGLE_DRIVE_FOLDER_ID")
    credentials_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    
    if not folder_id:
        logger.error("Google Drive folder ID not set in environment variables")
        return False
        
    if not credentials_json:
        logger.error("Google Drive credentials not set in environment variables")
        return False
    
    logger.info("✅ Google Drive credentials are configured")
    
    # Try to parse the credentials JSON
    try:
        credentials_data = json.loads(credentials_json)
        logger.info(f"✅ Credentials JSON parsed successfully (project_id: {credentials_data.get('project_id')})")
        return True
    except json.JSONDecodeError as e:
        logger.error(f"❌ Failed to parse credentials JSON: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_google_drive_credentials()
    sys.exit(0 if success else 1)
