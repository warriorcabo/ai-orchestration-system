# google_drive_storage.py
import os
import io
import json
import logging
import datetime
from typing import Dict, Any, List, Optional, BinaryIO, Union
import time
import ssl

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from googleapiclient.errors import HttpError

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
        
        # Maximum retries for transient errors
        self.max_retries = 3
        
        # Get credentials
        self._initialize_service()

    def _initialize_service(self):
        """Initialize Google Drive service with error handling and retries"""
        # SSL context setup to handle SSL issues
        try:
            # Default SSL context
            ssl._create_default_https_context = ssl._create_unverified_context
            logger.info("Using unverified SSL context to avoid SSL certificate issues")
        except Exception as e:
            logger.warning(f"Could not set SSL context: {str(e)}")
            
        # Initialize service with retries
        for attempt in range(self.max_retries):
            try:
                # Try to use service account if available
                credentials_path = os.environ.get("GOOGLE_CREDENTIALS_PATH", "credentials.json")
                if os.path.exists(credentials_path):
                    self.credentials = service_account.Credentials.from_service_account_file(
                        credentials_path,
                        scopes=['https://www.googleapis.com/auth/drive']
                    )
                    self.service = build('drive', 'v3', credentials=self.credentials)
                    logger.info("Google Drive service initialized with service account")
                    return
                else:
                    # Fallback to API key authentication (read-only)
                    api_key = os.environ.get("GOOGLE_API_KEY")
                    if api_key:
                        self.service = build('drive', 'v3', developerKey=api_key)
                        logger.info("Google Drive service initialized with API key (read-only)")
                        return
                    else:
                        raise ValueError("No Google Drive credentials or API key found")
            except ssl.SSLError as e:
                if attempt < self.max_retries - 1:
                    logger.warning(f"SSL Error (attempt {attempt+1}): {str(e)}. Retrying...")
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"SSL Error after {self.max_retries} attempts: {str(e)}")
                    log_error("google_drive_storage", f"SSL initialization error: {str(e)}")
                    raise
            except Exception as e:
                logger.error(f"Failed to initialize Google Drive service: {str(e)}")
                log_error("google_drive_storage", f"Init error: {str(e)}")
                raise

    def upload_text_file(self, content: str, filename: str, folder_id: Optional[str] = None,
                       mime_type: str = "text/plain") -> str:
        """Upload a text file to Google Drive with retry logic"""
        if not folder_id:
            folder_id = self.root_folder_id
            
        # Retry logic for transient errors
        for attempt in range(self.max_retries):
            try:
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

                logger.info(f"File uploaded successfully with ID: {file.get('id')}")
                return file.get('id')
                
            except ssl.SSLError as e:
                if attempt < self.max_retries - 1:
                    logger.warning(f"SSL Error during file upload (attempt {attempt+1}): {str(e)}. Retrying...")
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"SSL Error after {self.max_retries} attempts: {str(e)}")
                    log_error("google_drive_storage", f"SSL upload error: {str(e)}")
                    raise
            except HttpError as e:
                logger.error(f"HTTP Error during file upload: {str(e)}")
                log_error("google_drive_storage", f"HTTP upload error: {str(e)}")
                raise
            except Exception as e:
                logger.error(f"Failed to upload text file: {str(e)}")
                log_error("google_drive_storage", f"Upload error: {str(e)}")
                raise

    def create_folder(self, folder_name: str, parent_id: Optional[str] = None) -> str:
        """Create a new folder in Google Drive with retry logic"""
        if not parent_id:
            parent_id = self.root_folder_id
            
        # Retry logic for transient errors
        for attempt in range(self.max_retries):
            try:
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
                
            except ssl.SSLError as e:
                if attempt < self.max_retries - 1:
                    logger.warning(f"SSL Error during folder creation (attempt {attempt+1}): {str(e)}. Retrying...")
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"SSL Error after {self.max_retries} attempts: {str(e)}")
                    log_error("google_drive_storage", f"SSL folder creation error: {str(e)}")
                    raise
            except Exception as e:
                logger.error(f"Failed to create folder: {str(e)}")
                log_error("google_drive_storage", f"Folder creation error: {str(e)}")
                raise

    def get_or_create_folder(self, folder_name: str, parent_id: Optional[str] = None) -> str:
        """Get an existing folder or create it if it doesn't exist"""
        if not parent_id:
            parent_id = self.root_folder_id

        # Retry logic for transient errors
        for attempt in range(self.max_retries):
            try:
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
                
            except ssl.SSLError as e:
                if attempt < self.max_retries - 1:
                    logger.warning(f"SSL Error during folder operation (attempt {attempt+1}): {str(e)}. Retrying...")
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"SSL Error after {self.max_retries} attempts: {str(e)}")
                    log_error("google_drive_storage", f"SSL folder error: {str(e)}")
                    raise
            except Exception as e:
                logger.error(f"Failed to get or create folder: {str(e)}")
                log_error("google_drive_storage", f"Folder error: {str(e)}")
                raise

    def save_ai_output(self, content: str, user_id: str, query_type: str, format_type: str = "text") -> str:
        """Save AI-generated output with organized folder structure and naming"""
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

            # Return the file ID
            return file_id

        except Exception as e:
            logger.error(f"Failed to save AI output: {str(e)}")
            log_error("google_drive_storage", f"Save output error: {str(e)}")
            # Return a fallback message in case of error - don't crash the whole system
            return f"Error saving output: {str(e)}"

    def get_file_content(self, file_id: str) -> str:
        """Get the content of a file by ID with retry logic"""
        # Retry logic for transient errors
        for attempt in range(self.max_retries):
            try:
                # Get file metadata
                file = self.service.files().get(fileId=file_id).execute()

                # Download the file content
                request = self.service.files().get_media(fileId=file_id)
                content = request.execute()

                # Return content as string
                if isinstance(content, bytes):
                    return content.decode('utf-8')
                return content
                
            except ssl.SSLError as e:
                if attempt < self.max_retries - 1:
                    logger.warning(f"SSL Error during file download (attempt {attempt+1}): {str(e)}. Retrying...")
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.error(f"SSL Error after {self.max_retries} attempts: {str(e)}")
                    log_error("google_drive_storage", f"SSL download error: {str(e)}")
                    raise
            except Exception as e:
                logger.error(f"Failed to get file content: {str(e)}")
                log_error("google_drive_storage", f"File content error: {str(e)}")
                raise
