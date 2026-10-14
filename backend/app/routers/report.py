from fastapi import APIRouter, Depends, HTTPException, status
from app.models.detection import DetectionResult
from app.core.database import get_database
from app.middleware.auth_guard import get_current_user

router = APIRouter(prefix="/report", tags=["Report"])

@router.get("/{detection_id}", response_model=DetectionResult)
async def get_report(detection_id: str, current_user: dict = Depends(get_current_user)):
    db = get_database()
    if db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")

    try:
        from bson import ObjectId
        # Scoped to current_user to prevent access to other users' reports
        doc = await db.detections.find_one({"_id": ObjectId(detection_id), "user_id": current_user.get("id")})
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid report ID format")

    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report record not found or unauthorized")

    doc["id"] = str(doc["_id"])
    return DetectionResult(**doc)
