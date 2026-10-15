import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, status, Depends
from app.models.upload import UploadResponse
from app.services.gdrive import gdrive_service
from app.core.database import get_database
from app.middleware.auth_guard import get_current_user_optional
from app.core.config import settings

router = APIRouter(tags=["Upload"])

@router.post("/api/upload", response_model=UploadResponse)
@router.post("/upload", response_model=UploadResponse)
async def upload_file(
    file: UploadFile = File(...),
    type: str = Form(default="image"),
    current_user: dict = Depends(get_current_user_optional)
):
    contents = await file.read()

    upload_id = str(uuid.uuid4())
    unique_filename = f"{int(datetime.now().timestamp() * 1000)}-{file.filename}"
    
    # Attempt upload to Google Drive
    gdrive_result = None
    storage_type = "memory"
    gdrive_file_id = None

    if gdrive_service.is_available:
        try:
            gdrive_result = await gdrive_service.upload_file(
                file_bytes=contents,
                filename=unique_filename,
                mime_type=file.content_type or "application/octet-stream"
            )
            if not gdrive_result or not gdrive_result.get("id"):
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail="Google Drive rejected the file upload."
                )
            storage_type = "gdrive"
            gdrive_file_id = gdrive_result.get("id")
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Google Drive upload failed: {str(e)}"
            )

    # Persist metadata to MongoDB if available
    db = get_database()
    if db is not None:
        user_id = current_user.get("id") if current_user else None
        metadata = {
            "upload_id": upload_id,
            "user_id": user_id,
            "filename": unique_filename,
            "original_name": file.filename,
            "content_type": file.content_type,
            "file_type": type,
            "size_bytes": size_bytes,
            "gdrive_file_id": gdrive_file_id,
            "storage_type": storage_type,
            "is_public": False,
            "created_at": datetime.now(timezone.utc)
        }
        try:
            await db.uploads.insert_one(metadata)
        except Exception:
            pass

    return UploadResponse(
        success=True,
        upload_id=upload_id,
        filename=unique_filename,
        original_name=file.filename or "",
        size=size_bytes,
        type=type,
        storage=storage_type
    )
