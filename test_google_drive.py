# test_google_drive.py

import os
import sys
import logging
import json
import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import the Google Drive storage module
from src.utils.google_drive_storage import GoogleDriveStorage

def test_google_drive_storage():
    """Test the Google Drive storage integration"""
    logger.info("Testing Google Drive Storage...")

    # Initialize the storage
    storage = GoogleDriveStorage()

    # Check if Google Drive is available
    if not storage.is_available:
        logger.error("Google Drive is not available. Check credentials and permissions.")
        return False

    # Create a test file
    test_content = {
        "test": True,
        "timestamp": str(datetime.datetime.now()),
        "message": "This is a test file from the AI Orchestration System"
    }

    try:
        # Save to Google Drive
        file_id = storage.save_ai_output(
            content=json.dumps(test_content, indent=2),
            user_id="test_user",
            query_type="test_drive_integration",
            format_type="json"
        )

        logger.info(f"Saved test file with reference: {file_id}")

        if file_id and not file_id.startswith("error:"):
            logger.info("✅ Google Drive integration test successful!")
            return True
        else:
            logger.error(f"❌ Google Drive integration test failed with result: {file_id}")
            return False
    except Exception as e:
        logger.error(f"❌ Google Drive test failed with exception: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_google_drive_storage()
    sys.exit(0 if success else 1)
