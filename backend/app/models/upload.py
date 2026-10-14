from datetime import datetime, timezone
from typing import Optional
from pydantic import BaseModel, Field

class UploadMetadata(BaseModel):
    id: Optional[str] = Field(default=None, alias="_id")
    user_id: Optional[str] = None
    filename: str
    original_name: str
    content_type: str
    file_type: str  # image, text, document, video
    size_bytes: int
    gdrive_file_id: Optional[str] = None
    local_path: Optional[str] = None
    is_public: bool = False
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    class Config:
        populate_by_name = True

class UploadResponse(BaseModel):
    success: bool
    upload_id: str
    filename: str
    original_name: str
    size: int
    type: str
    storage: str  # "gdrive" | "local" | "memory"
