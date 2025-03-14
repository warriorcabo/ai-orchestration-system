# direct_drive_test.py

import os
import sys
import json
import logging
import datetime
from src.utils.google_drive_storage import GoogleDriveStorage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_direct_drive():
    """Test direct Google Drive storage"""
    logger.info("Testing direct Google Drive storage...")
    
    # Create storage
    storage = GoogleDriveStorage()
    
    # Check if available
    if not storage.is_available:
        logger.error("Google Drive is not available")
        return False
    
    # Create test content
    test_content = {
        "test_id": "direct_test",
        "timestamp": datetime.datetime.now().isoformat(),
        "message": "This is a direct test from the AI Orchestration System"
    }
    
    # Save to Google Drive
    try:
        file_id = storage.save_ai_output(
            content=json.dumps(test_content, indent=2),
            user_id="direct_test_user",
            query_type="direct_test",
            format_type="json"
        )
        
        logger.info(f"Saved file to Google Drive: {file_id}")
        
        if file_id.startswith("google_drive:"):
            file_id = file_id.replace("google_drive:", "")
            logger.info(f"File ID: {file_id}")
            logger.info("View in Google Drive: https://drive.google.com/file/d/{}/view".format(file_id))
            
            return True
        else:
            logger.error(f"Failed to save file: {file_id}")
            return False
            
    except Exception as e:
        logger.error(f"Error testing Google Drive: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_direct_drive()
    sys.exit(0 if success else 1)
