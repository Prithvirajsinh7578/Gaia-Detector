import io
import json
import logging
from typing import Optional, Dict, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

class GoogleDriveService:
    def __init__(self):
        self.service = None
        self._init_service()

    def _init_service(self):
        if not settings.is_gdrive_configured:
            logger.info("Google Drive is not fully configured (using placeholders/missing credentials).")
            return

        try:
            from google.oauth2 import service_account
            from googleapiclient.discovery import build

            scopes = [
                "https://www.googleapis.com/auth/drive",
                "https://www.googleapis.com/auth/drive.file"
            ]
            creds = None
            if settings.GOOGLE_SERVICE_ACCOUNT_JSON_PATH:
                creds = service_account.Credentials.from_service_account_file(
                    settings.GOOGLE_SERVICE_ACCOUNT_JSON_PATH,
                    scopes=scopes
                )
            elif settings.GOOGLE_SERVICE_ACCOUNT_JSON_CONTENT:
                info = json.loads(settings.GOOGLE_SERVICE_ACCOUNT_JSON_CONTENT)
                creds = service_account.Credentials.from_service_account_info(
                    info,
                    scopes=scopes
                )

            if creds:
                self.service = build("drive", "v3", credentials=creds)
                logger.info("Google Drive API service initialized with Shared Drive support.")
        except Exception as e:
            logger.error(f"Failed to initialize Google Drive service: {e}")
            self.service = None

    @property
    def is_available(self) -> bool:
        return self.service is not None

    async def upload_file(
        self,
        file_bytes: bytes,
        filename: str,
        mime_type: str,
        folder_id: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        if not self.is_available:
            logger.warning("Google Drive service not available. Skipping Drive upload.")
            return None

        try:
            from googleapiclient.http import MediaIoBaseUpload

            target_folder = folder_id or settings.GOOGLE_DRIVE_FOLDER_ID
            file_metadata = {
                "name": filename,
                "parents": [target_folder] if target_folder else []
            }
            media = MediaIoBaseUpload(
                io.BytesIO(file_bytes),
                mimetype=mime_type,
                resumable=True
            )

            # Files in Shared Drives require supportsAllDrives=True
            created = self.service.files().create(
                body=file_metadata,
                media_body=media,
                supportsAllDrives=True,
                fields="id, name, mimeType, webViewLink, size, parents, driveId"
            ).execute()

            logger.info(f"File uploaded to Google Drive with ID: {created.get('id')}")
            return created
        except Exception as e:
            logger.error(f"Error uploading file to Google Drive: {e}")
            raise e

    def get_file(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve file metadata from Google Drive (supporting Shared Drives)."""
        if not self.is_available:
            return None
        try:
            return self.service.files().get(
                fileId=file_id,
                supportsAllDrives=True,
                fields="id, name, mimeType, webViewLink, size, parents, driveId, trashed"
            ).execute()
        except Exception as e:
            logger.error(f"Error retrieving file from Google Drive: {e}")
            return None

    def delete_file(self, file_id: str) -> bool:
        """
        Delete or trash file in Google Drive.
        In Shared Drives, Content Managers can trash files, while Managers can permanently delete.
        """
        if not self.is_available:
            return False
        try:
            # First attempt permanent deletion
            self.service.files().delete(
                fileId=file_id,
                supportsAllDrives=True
            ).execute()
            logger.info(f"File {file_id} permanently deleted from Google Drive.")
            return True
        except Exception as del_err:
            logger.warning(f"Permanent delete failed ({del_err}), attempting to move to trash...")
            try:
                # Content Manager role in Shared Drives permits trashing
                self.service.files().update(
                    fileId=file_id,
                    body={"trashed": True},
                    supportsAllDrives=True
                ).execute()
                logger.info(f"File {file_id} moved to trash in Google Drive.")
                return True
            except Exception as trash_err:
                logger.error(f"Failed to trash file {file_id}: {trash_err}")
                return False

gdrive_service = GoogleDriveService()
