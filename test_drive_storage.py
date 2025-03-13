# test_drive_storage.py

import os
import sys
import json
import logging
import datetime
from src.utils.google_drive_storage import GoogleDriveStorage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_google_drive_storage():
    """Test Google Drive storage functionality"""
    logger.info("Testing Google Drive storage...")
    
    # Initialize storage
    storage = GoogleDriveStorage()
    
    # Check if available
    if not storage.is_available:
        logger.error("Google Drive storage not available")
        return False
        
    try:
        # Create a test content
        test_content = {
            "test_id": "drive_test",
            "timestamp": datetime.datetime.now().isoformat(),
            "message": "This is a test from the AI Orchestration System"
        }
        
        # Save to Google Drive
        file_id = storage.save_ai_output(
            content=json.dumps(test_content, indent=2),
            user_id="test_user",
            query_type="drive_test",
            format_type="json"
        )
        
        logger.info(f"Saved test file with ID: {file_id}")
        
        # Check if successful
        if file_id and not file_id.startswith("error:"):
            logger.info("✅ Google Drive storage test successful!")
            return True
        else:
            logger.error(f"❌ Google Drive storage test failed with result: {file_id}")
            return False
    
    except Exception as e:
        logger.error(f"❌ Error testing Google Drive storage: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_google_drive_storage()
    sys.exit(0 if success else 1)
