# google_drive_storage.py
import os
import json
import logging
import datetime
import io
from typing import Dict, Any, List, Optional, BinaryIO, Union

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload

from utils.error_handler import log_error

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class GoogleDriveStorage:
    """Manager for Google Drive storage operations"""

    def __init__(self):
        """Initialize the Google Drive connector"""
        # Root folder ID for all AI outputs
        self.root_folder_id = os.environ.get("GOOGLE_DRIVE_FOLDER_ID", "16OQvIr6VOE4kUjEX4AJCzIJ-GDyr-aOB")
        
        # Flag to track availability
        self.is_available = False

        # Get credentials
        try:
            # First try to get JSON credentials from environment
            credentials_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
            credentials_path = os.environ.get("GOOGLE_CREDENTIALS_PATH", "credentials.json")
            
            if credentials_json:
                # Parse JSON directly from environment variable
                info = json.loads(credentials_json)
                self.credentials = service_account.Credentials.from_service_account_info(
                    info,
                    scopes=['https://www.googleapis.com/auth/drive']
                )
                self.service = build('drive', 'v3', credentials=self.credentials)
                self.is_available = True
                logger.info("Google Drive initialized using credentials from environment")
            elif os.path.exists(credentials_path):
                # Fallback to credentials file
                self.credentials = service_account.Credentials.from_service_account_file(
                    credentials_path,
                    scopes=['https://www.googleapis.com/auth/drive']
                )
                self.service = build('drive', 'v3', credentials=self.credentials)
                self.is_available = True
                logger.info("Google Drive initialized using credentials file")
            else:
                # Fallback to API key authentication (read-only)
                api_key = os.environ.get("GOOGLE_API_KEY")
                if api_key:
                    self.service = build('drive', 'v3', developerKey=api_key)
                    self.is_available = True
                    logger.info("Google Drive initialized using API key (read-only)")
                else:
                    logger.warning("No Google Drive credentials or API key found")
        except Exception as e:
            logger.error(f"Failed to initialize Google Drive service: {str(e)}")
            log_error("google_drive_storage", f"Init error: {str(e)}")
            self.is_available = False
    
    def upload_text_file(self, content: str, filename: str, folder_id: Optional[str] = None,
                       mime_type: str = "text/plain") -> str:
        """Upload a text file to Google Drive"""
        try:
            # Use specified folder or default to root folder
            if not folder_id:
                folder_id = self.root_folder_id

            # Create file metadata
            file_metadata = {
                'name': filename,
                'parents': [folder_id],
                'mimeType': mime_type
            }

            # Create media
            media = MediaIoBaseUpload(
                io.BytesIO(content.encode('utf-8')),
                mimetype=mime_type,
                resumable=True
            )

            # Create the file
            file = self.service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()

            logger.info(f"File created with ID: {file.get('id')}")
            return f"google_drive:{file.get('id')}"

        except Exception as e:
            logger.error(f"Failed to upload text file: {str(e)}")
            log_error("google_drive_storage", f"Upload error: {str(e)}")
            return f"error:{str(e)}"
            
    def save_ai_output(self, content: str, user_id: str, query_type: str, format_type: str = "text") -> str:
        """Save AI-generated output with organized folder structure and naming"""
        try:
            if not self.is_available:
                logger.warning("Google Drive is not available")
                return "error:google_drive_not_available"
                
            # Create timestamp for filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

            # Create user folder if it doesn't exist
            user_folder_id = self.get_or_create_folder(f"user_{user_id}")

            # Create query type subfolder
            type_folder_id = self.get_or_create_folder(query_type, user_folder_id)

            # Create filename with timestamp
            sanitized_query = query_type.replace(" ", "_").lower()[:30]  # Limit length and sanitize
            filename = f"{sanitized_query}_{timestamp}"

            # Add appropriate extension based on format
            if format_type == "text":
                filename += ".txt"
                mime_type = "text/plain"
            elif format_type == "markdown":
                filename += ".md"
                mime_type = "text/markdown"
            elif format_type == "json":
                filename += ".json"
                mime_type = "application/json"
            elif format_type == "html":
                filename += ".html"
                mime_type = "text/html"
            else:
                filename += ".txt"
                mime_type = "text/plain"

            # Upload the file
            file_id = self.upload_text_file(content, filename, type_folder_id, mime_type)

            # Return the file ID
            return file_id

        except Exception as e:
            logger.error(f"Failed to save AI output: {str(e)}")
            log_error("google_drive_storage", f"Save output error: {str(e)}")
            return f"error:{str(e)}"
            
    def get_or_create_folder(self, folder_name: str, parent_id: Optional[str] = None) -> str:
        """Get an existing folder or create it if it doesn't exist"""
        try:
            # Use specified parent or default to root folder
            if not parent_id:
                parent_id = self.root_folder_id

            # Search for the folder
            query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and '{parent_id}' in parents and trashed = false"
            results = self.service.files().list(
                q=query,
                spaces='drive',
                fields='files(id, name)'
            ).execute()

            items = results.get('files', [])

            # Return existing folder ID if found
            if items:
                return items[0]['id']

            # Create new folder if not found
            return self.create_folder(folder_name, parent_id)

        except Exception as e:
            logger.error(f"Failed to get or create folder: {str(e)}")
            log_error("google_drive_storage", f"Folder error: {str(e)}")
            raise
            
    def create_folder(self, folder_name: str, parent_id: Optional[str] = None) -> str:
        """Create a new folder in Google Drive"""
        try:
            # Use specified parent or default to root folder
            if not parent_id:
                parent_id = self.root_folder_id

            # Create folder metadata
            folder_metadata = {
                'name': folder_name,
                'parents': [parent_id],
                'mimeType': 'application/vnd.google-apps.folder'
            }

            # Create the folder
            folder = self.service.files().create(
                body=folder_metadata,
                fields='id'
            ).execute()

            logger.info(f"Folder created with ID: {folder.get('id')}")
            return folder.get('id')

        except Exception as e:
            logger.error(f"Failed to create folder: {str(e)}")
            log_error("google_drive_storage", f"Folder creation error: {str(e)}")
            raise
