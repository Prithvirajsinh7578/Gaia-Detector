from datetime import datetime, timezone
from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from app.models.detection import DetectionRequestText, DetectionResult
from app.services.ai_detector import detector_service
from app.core.database import get_database
from app.middleware.auth_guard import get_current_user_optional

router = APIRouter(prefix="/detect", tags=["Detection"])

async def save_detection_record(result_dict: dict, user_id: str = None, upload_id: str = None, filename: str = None):
    record = result_dict.copy()
    record["user_id"] = user_id
    record["upload_id"] = upload_id
    record["filename"] = filename
    record["created_at"] = datetime.now(timezone.utc)
    db = get_database()
    if db is not None:
        try:
            insert_res = await db.detections.insert_one(record)
            record["id"] = str(insert_res.inserted_id)
            record["_id"] = str(insert_res.inserted_id)
        except Exception:
            pass
    return record

@router.post("/image", response_model=DetectionResult)
async def detect_image(
    file: UploadFile = File(...),
    upload_id: str = Form(default=None),
    current_user: dict = Depends(get_current_user_optional)
):
    image_bytes = await file.read()
    user_id = current_user.get("id") if current_user else None

    # Initialise storage metadata — will be populated if we auto-upload below.
    storage_type: str = "memory"
    gdrive_file_id: str | None = None

    # If file was not previously uploaded via /upload, store it to Google Drive / storage now
    if not upload_id:
        import uuid
        from app.services.gdrive import gdrive_service
        auto_upload_id = str(uuid.uuid4())
        unique_filename = f"{int(datetime.now().timestamp() * 1000)}-{file.filename}"

        if gdrive_service.is_available:
            try:
                gdrive_result = await gdrive_service.upload_file(
                    file_bytes=image_bytes,
                    filename=unique_filename,
                    mime_type=file.content_type or "image/png"
                )
                if not gdrive_result or not gdrive_result.get("id"):
                    raise HTTPException(
                        status_code=502,
                        detail="Google Drive rejected the file upload."
                    )
                storage_type = "gdrive"
                gdrive_file_id = gdrive_result.get("id")
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=502,
                    detail=f"Google Drive upload failed: {str(e)}"
                )

        db = get_database()
        if db is not None:
            upload_meta = {
                "upload_id": auto_upload_id,
                "user_id": user_id,
                "filename": unique_filename,
                "original_name": file.filename,
                "content_type": file.content_type or "image/png",
                "file_type": "image",
                "size_bytes": len(image_bytes),
                "gdrive_file_id": gdrive_file_id,
                "storage_type": storage_type,
                "is_public": False,
                "created_at": datetime.now(timezone.utc)
            }
            try:
                await db.uploads.insert_one(upload_meta)
            except Exception:
                pass
        upload_id = auto_upload_id

    result = detector_service.detect_image(image_bytes)
    # Always surface storage metadata in the detection response
    result["storage_type"] = storage_type
    result["gdrive_file_id"] = gdrive_file_id
    saved = await save_detection_record(result, user_id=user_id, upload_id=upload_id, filename=file.filename)
    return DetectionResult(**saved)

@router.post("/text", response_model=DetectionResult)
async def detect_text(
    payload: DetectionRequestText,
    current_user: dict = Depends(get_current_user_optional)
):
    result = detector_service.detect_text(payload.text)
    user_id = current_user.get("id") if current_user else None
    saved = await save_detection_record(result, user_id=user_id, filename="Raw text input")
    return DetectionResult(**saved)

@router.post("/document", response_model=DetectionResult)
async def detect_document(
    file: UploadFile = File(...),
    upload_id: str = Form(default=None),
    current_user: dict = Depends(get_current_user_optional)
):
    doc_bytes = await file.read()
    result = detector_service.detect_document(doc_bytes, file.filename or "doc.pdf")
    user_id = current_user.get("id") if current_user else None
    saved = await save_detection_record(result, user_id=user_id, upload_id=upload_id, filename=file.filename)
    return DetectionResult(**saved)

@router.post("/video", response_model=DetectionResult)
async def detect_video(
    file: UploadFile = File(...),
    upload_id: str = Form(default=None),
    current_user: dict = Depends(get_current_user_optional)
):
    video_bytes = await file.read()
    result = detector_service.detect_video(video_bytes, file.filename or "video.mp4")
    user_id = current_user.get("id") if current_user else None
    saved = await save_detection_record(result, user_id=user_id, upload_id=upload_id, filename=file.filename)
    return DetectionResult(**saved)
