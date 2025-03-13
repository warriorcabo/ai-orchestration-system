# upload_credentials.py

import os
import sys
import json
import base64
import logging
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def setup_google_drive():
    """Set up Google Drive with direct credentials file"""
    logger.info("Setting up Google Drive...")
    
    # Service account file path - handle BOM correctly
    service_account_file = "flexmls-scraper-1c4b02856bed.json"
    folder_id = os.environ.get("GOOGLE_DRIVE_FOLDER_ID", "16OQvIr6VOE4kUjEX4AJCzIJ-GDyr-aOB")
    
    try:
        # Read and parse the file with BOM handling
        with open(service_account_file, 'r', encoding='utf-8-sig') as f:
            credentials_data = json.load(f)
        
        # Create credentials from parsed data
        credentials = service_account.Credentials.from_service_account_info(
            credentials_data,
            scopes=['https://www.googleapis.com/auth/drive']
        )
        
        # Build the service
        service = build('drive', 'v3', credentials=credentials)
        
        # Create a test folder
        folder_metadata = {
            'name': 'ai_orchestration_system',
            'mimeType': 'application/vnd.google-apps.folder',
            'parents': [folder_id]
        }
        
        # Check if folder already exists
        query = f"name='ai_orchestration_system' and mimeType='application/vnd.google-apps.folder' and '{folder_id}' in parents and trashed=false"
        results = service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        items = results.get('files', [])
        
        if items:
            folder_id = items[0]['id']
            logger.info(f"Using existing folder: {folder_id}")
        else:
            folder = service.files().create(body=folder_metadata, fields='id').execute()
            folder_id = folder.get('id')
            logger.info(f"Created new folder: {folder_id}")
        
        # Create a test file
        file_metadata = {
            'name': 'test_connection.txt',
            'parents': [folder_id]
        }
        
        media = MediaFileUpload(
            "test_connection.txt",
            mimetype='text/plain',
            resumable=True
        )
        
        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        logger.info(f"Created test file: {file.get('id')}")
        
        logger.info("✅ Google Drive setup successful!")
        return True
    except Exception as e:
        logger.error(f"Error setting up Google Drive: {str(e)}")
        return False

if __name__ == "__main__":
    # Create a test file
    with open("test_connection.txt", "w") as f:
        f.write(f"Test connection from AI Orchestration System at {os.environ.get('DYNO', 'local')}")
    
    success = setup_google_drive()
    sys.exit(0 if success else 1)
