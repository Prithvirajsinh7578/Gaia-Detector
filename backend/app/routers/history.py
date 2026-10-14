from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from app.models.detection import HistoryItem, DetectionResult
from app.core.database import get_database
from app.middleware.auth_guard import get_current_user

router = APIRouter(prefix="/history", tags=["History"])

@router.get("", response_model=List[HistoryItem])
async def get_history(
    limit: int = Query(default=20, ge=1, le=100),
    skip: int = Query(default=0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    db = get_database()
    if db is None:
        return []

    user_id = current_user.get("id")
    # Strictly scoped to current_user
    cursor = db.detections.find({"user_id": user_id}).sort("created_at", -1).skip(skip).limit(limit)
    
    items = []
    async for doc in cursor:
        items.append(
            HistoryItem(
                id=str(doc["_id"]),
                content_type=doc.get("content_type", "unknown"),
                prediction=doc.get("prediction", "Unknown"),
                confidence=float(doc.get("confidence", 0.0)),
                status=doc.get("status", "Analyzed"),
                risk_level=doc.get("risk_level", "Unknown"),
                created_at=doc.get("created_at"),
                filename=doc.get("filename")
            )
        )
    return items

@router.get("/{detection_id}", response_model=DetectionResult)
async def get_history_detail(detection_id: str, current_user: dict = Depends(get_current_user)):
    db = get_database()
    if db is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Record not found")

    try:
        from bson import ObjectId
        # Scoped to current_user to prevent ID guessing
        doc = await db.detections.find_one({"_id": ObjectId(detection_id), "user_id": current_user.get("id")})
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid detection ID format")

    if not doc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Detection record not found or unauthorized")

    doc["id"] = str(doc["_id"])
    return DetectionResult(**doc)
