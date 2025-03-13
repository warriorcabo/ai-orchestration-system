# bom_handling_test.py

import os
import sys
import json
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_google_drive():
    """Test Google Drive connection with BOM handling"""
    logger.info("Testing Google Drive connection...")
    
    # Service account file path
    service_account_file = "flexmls-scraper-1c4b02856bed.json"
    folder_id = "16OQvIr6VOE4kUjEX4AJCzIJ-GDyr-aOB"
    
    try:
        # First, let's verify the file exists and check its content
        if not os.path.exists(service_account_file):
            logger.error(f"Service account file not found: {service_account_file}")
            return False
            
        # Read file with BOM handling
        with open(service_account_file, 'r', encoding='utf-8-sig') as f:
            credentials_data = json.load(f)
            logger.info(f"Successfully loaded credentials (project_id: {credentials_data.get('project_id')})")
        
        # Create credentials from parsed data
        credentials = service_account.Credentials.from_service_account_info(
            credentials_data,
            scopes=['https://www.googleapis.com/auth/drive']
        )
        
        # Build the service
        service = build('drive', 'v3', credentials=credentials)
        
        # Test connection by listing files
        results = service.files().list(
            q=f"'{folder_id}' in parents",
            pageSize=10,
            fields="nextPageToken, files(id, name)"
        ).execute()
        
        items = results.get('files', [])
        
        if not items:
            logger.info("No files found.")
        else:
            logger.info("Files:")
            for item in items:
                logger.info(f"{item['name']} ({item['id']})")
                
        logger.info("✅ Google Drive connection successful!")
        return True
        
    except Exception as e:
        logger.error(f"Error connecting to Google Drive: {str(e)}")
        logger.error(f"Exception type: {type(e).__name__}")
        return False

if __name__ == "__main__":
    success = test_google_drive()
    sys.exit(0 if success else 1)
