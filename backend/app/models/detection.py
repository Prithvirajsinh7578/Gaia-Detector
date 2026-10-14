from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

class DetectionRequestText(BaseModel):
    text: str

class DetectionResult(BaseModel):
    id: Optional[str] = None
    user_id: Optional[str] = None
    upload_id: Optional[str] = None
    content_type: str  # image, text, document, video
    status: str  # e.g., "Likely AI Generated", "Likely Real", "Not Implemented"
    prediction: str  # e.g., "Likely AI", "Likely Real"
    confidence: float  # 0 to 100
    processing_time_sec: float
    risk_level: str  # "Low" | "Medium" | "High" | "Unknown"
    summary: str
    detector_name: str
    verified: bool = False
    details: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    # Cloud storage metadata surfaced in API response
    storage_type: Optional[str] = None   # "gdrive" | "memory"
    gdrive_file_id: Optional[str] = None

    def __init__(self, **data):
        if "_id" in data and ("id" not in data or not data["id"]):
            data["id"] = str(data["_id"])
        elif "id" in data and data["id"] is not None:
            data["id"] = str(data["id"])
        super().__init__(**data)

class HistoryItem(BaseModel):
    id: str
    content_type: str
    prediction: str
    confidence: float
    status: str
    risk_level: str
    created_at: datetime
    filename: Optional[str] = None
