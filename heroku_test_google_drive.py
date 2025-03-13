# heroku_test_google_drive.py

import os
import sys
import json
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_google_drive_remote():
    """Test Google Drive connection on Heroku"""
    logger.info("Testing Google Drive connection on Heroku...")
    
    # Get credentials from environment
    credentials_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
    folder_id = os.environ.get("GOOGLE_DRIVE_FOLDER_ID")
    
    if not credentials_json:
        logger.error("GOOGLE_CREDENTIALS_JSON not set")
        return False
        
    if not folder_id:
        logger.error("GOOGLE_DRIVE_FOLDER_ID not set")
        return False
    
    try:
        # Parse credentials
        info = json.loads(credentials_json)
        credentials = service_account.Credentials.from_service_account_info(
            info, scopes=['https://www.googleapis.com/auth/drive']
        )
        
        # Build the service
        service = build('drive', 'v3', credentials=credentials)
        
        # List files in the root folder
        results = service.files().list(
            q=f"'{folder_id}' in parents",
            pageSize=10,
            fields="nextPageToken, files(id, name, mimeType)"
        ).execute()
        
        files = results.get('files', [])
        
        if not files:
            logger.info("No files found in the folder.")
        else:
            logger.info("Files in the folder:")
            for file in files:
                logger.info(f"{file['name']} ({file['id']})")
        
        # Create a test folder
        folder_metadata = {
            'name': 'test_folder_' + os.environ.get('DYNO', 'local'),
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [folder_id]
        }
        
        folder = service.files().create(
            body=folder_metadata, fields='id'
        ).execute()
        
        logger.info(f"Created test folder with ID: {folder.get('id')}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error testing Google Drive: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_google_drive_remote()
    sys.exit(0 if success else 1)
