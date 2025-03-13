# src/utils/google_drive_storage.py

import os
import logging
import datetime
import io
import json
from typing import Dict, Any, Optional, BinaryIO

# Import Google Drive API libraries if available
try:
    from google.oauth2 import service_account
    from googleapiclient.discovery import build
    from googleapiclient.http import MediaIoBaseUpload
    GOOGLE_LIBS_AVAILABLE = True
except ImportError:
    GOOGLE_LIBS_AVAILABLE = False

from src.utils.error_handler import log_error

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
        # Check if Google libraries are available
        if not GOOGLE_LIBS_AVAILABLE:
            logger.warning("Google Drive API libraries not available. Using fallback storage.")
            self.service = None
            self.is_available = False
            return

        # Root folder ID for all AI outputs
        self.root_folder_id = os.environ.get("GOOGLE_DRIVE_FOLDER_ID", "16OQvIr6VOE4kUjEX4AJCzIJ-GDyr-aOB")

        # Get credentials
        try:
            # Check for credentials file
            credentials_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
            
            if credentials_path and os.path.exists(credentials_path):
                # Use service account from file
                self.credentials = service_account.Credentials.from_service_account_file(
                    credentials_path,
                    scopes=['https://www.googleapis.com/auth/drive']
                )
                self.service = build('drive', 'v3', credentials=self.credentials)
                self.is_available = True
                logger.info(f"Successfully initialized Google Drive storage with credentials file: {credentials_path}")
            else:
                # Try to use embedded credentials (for Heroku)
                try:
                    # Check if the credentials are directly in the environment
                    creds_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")
                    if creds_json:
                        creds_info = json.loads(creds_json)
                        self.credentials = service_account.Credentials.from_service_account_info(
                            creds_info,
                            scopes=['https://www.googleapis.com/auth/drive']
                        )
                        self.service = build('drive', 'v3', credentials=self.credentials)
                        self.is_available = True
                        logger.info("Successfully initialized Google Drive storage with credentials from environment")
                    else:
                        logger.warning("No Google Drive credentials found. Using fallback storage.")
                        self.service = None
                        self.is_available = False
                except Exception as e:
                    logger.error(f"Error loading credentials from environment: {str(e)}")
                    self.service = None
                    self.is_available = False
        except Exception as e:
            logger.error(f"Failed to initialize Google Drive service: {str(e)}")
            log_error("google_drive_storage", f"Init error: {str(e)}")
            self.service = None
            self.is_available = False

    def save_ai_output(self, content: str, user_id: str, query_type: str, format_type: str = "text") -> str:
        """Save AI-generated output with organized folder structure and naming"""
        if not self.is_available:
            return self._fallback_save(content, user_id, query_type, format_type)

        try:
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
            
            logger.info(f"Saved output to Google Drive with ID: {file_id}")
            return f"google_drive:{file_id}"

        except Exception as e:
            logger.error(f"Failed to save AI output: {str(e)}")
            log_error("google_drive_storage", f"Save output error: {str(e)}")
            return self._fallback_save(content, user_id, query_type, format_type)

    def _fallback_save(self, content: str, user_id: str, query_type: str, format_type: str = "text") -> str:
        """Fallback method to save content locally when Google Drive is unavailable"""
        try:
            # Create local logs directory if it doesn't exist
            local_dir = os.path.join("logs", "outputs", f"user_{user_id}")
            os.makedirs(local_dir, exist_ok=True)

            # Create timestamp for filename
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            sanitized_query = query_type.replace(" ", "_").lower()[:30]
            
            # Create filename with appropriate extension
            if format_type == "text":
                filename = f"{sanitized_query}_{timestamp}.txt"
            elif format_type == "markdown":
                filename = f"{sanitized_query}_{timestamp}.md"
            elif format_type == "json":
                filename = f"{sanitized_query}_{timestamp}.json"
            elif format_type == "html":
                filename = f"{sanitized_query}_{timestamp}.html"
            else:
                filename = f"{sanitized_query}_{timestamp}.txt"
            
            # Save to local file
            file_path = os.path.join(local_dir, filename)
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Saved output to local file: {file_path}")
            return f"local:{file_path}"
        
        except Exception as e:
            logger.error(f"Failed to save output locally: {str(e)}")
            return "save_failed"

    def upload_text_file(self, content: str, filename: str, folder_id: Optional[str] = None,
                        mime_type: str = "text/plain") -> str:
        """Upload a text file to Google Drive"""
        if not self.is_available:
            return "google_drive_not_available"

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
            return file.get('id')

        except Exception as e:
            logger.error(f"Failed to upload text file: {str(e)}")
            log_error("google_drive_storage", f"Upload error: {str(e)}")
            return "upload_failed"

    def get_or_create_folder(self, folder_name: str, parent_id: Optional[str] = None) -> str:
        """Get an existing folder or create it if it doesn't exist"""
        if not self.is_available:
            return "google_drive_not_available"

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
            return "folder_error"

    def create_folder(self, folder_name: str, parent_id: Optional[str] = None) -> str:
        """Create a new folder in Google Drive"""
        if not self.is_available:
            return "google_drive_not_available"

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
            return "folder_creation_failed"
