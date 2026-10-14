from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status, Response, Depends
from app.models.user import UserCreate, UserLogin, UserResponse
from app.core.security import hash_password, verify_password, create_access_token
from app.core.config import settings
from app.core.database import get_database
from app.middleware.auth_guard import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
async def register(user_data: UserCreate, response: Response):
    db = get_database()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection is not configured on this server."
        )

    existing = await db.users.find_one({"email": user_data.email})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )

    user_dict = {
        "email": user_data.email,
        "name": user_data.name,
        "hashed_password": hash_password(user_data.password),
        "created_at": datetime.now(timezone.utc)
    }

    result = await db.users.insert_one(user_dict)
    user_id = str(result.inserted_id)

    # Issue JWT in httpOnly cookie
    token = create_access_token({"sub": user_id, "email": user_data.email, "name": user_data.name})
    response.set_cookie(
        key=settings.COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.JWT_EXPIRY_MINUTES * 60,
    )

    return UserResponse(
        id=user_id,
        email=user_data.email,
        name=user_data.name,
        created_at=user_dict["created_at"]
    )

@router.post("/login", response_model=UserResponse)
async def login(credentials: UserLogin, response: Response):
    db = get_database()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Database connection is not configured on this server."
        )

    user = await db.users.find_one({"email": credentials.email})
    if not user or not verify_password(credentials.password, user.get("hashed_password", "")):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password."
        )

    user_id = str(user["_id"])
    token = create_access_token({"sub": user_id, "email": user["email"], "name": user.get("name", "")})

    # Set httpOnly cookie
    response.set_cookie(
        key=settings.COOKIE_NAME,
        value=token,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
        max_age=settings.JWT_EXPIRY_MINUTES * 60,
    )

    return UserResponse(
        id=user_id,
        email=user["email"],
        name=user.get("name", ""),
        created_at=user.get("created_at", datetime.now(timezone.utc))
    )

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(
        key=settings.COOKIE_NAME,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
    )
    return {"message": "Logged out successfully."}

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=current_user.get("id", str(current_user.get("_id", ""))),
        email=current_user["email"],
        name=current_user.get("name", ""),
        created_at=current_user.get("created_at", datetime.now(timezone.utc))
    )
