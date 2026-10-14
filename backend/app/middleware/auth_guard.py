from typing import Optional, Dict, Any
from fastapi import Request, HTTPException, status, Depends
from app.core.config import settings
from app.core.security import decode_access_token
from app.core.database import get_database

async def get_current_user_optional(request: Request) -> Optional[Dict[str, Any]]:
    # 1. Check httpOnly cookie first
    token = request.cookies.get(settings.COOKIE_NAME)
    
    # 2. Fallback to Authorization header (Bearer ...)
    if not token:
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

    if not token:
        return None

    payload = decode_access_token(token)
    if not payload:
        return None

    user_id = payload.get("sub")
    email = payload.get("email")
    if not user_id or not email:
        return None

    db = get_database()
    if db is not None:
        try:
            from bson import ObjectId
            user = await db.users.find_one({"_id": ObjectId(user_id)})
            if user:
                user["id"] = str(user["_id"])
                return user
        except Exception:
            pass

    # If DB not connected or user record format differs, return payload representation
    return {"id": user_id, "email": email, "name": payload.get("name", "")}

async def get_current_user(current_user: Optional[Dict[str, Any]] = Depends(get_current_user_optional)) -> Dict[str, Any]:
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required. Please log in.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    return current_user
