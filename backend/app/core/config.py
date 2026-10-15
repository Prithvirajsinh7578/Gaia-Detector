from typing import List
from pydantic_settings import BaseSettings
from pydantic import Field

class Settings(BaseSettings):
    # MongoDB
    MONGODB_URI: str = Field(default="mongodb+srv://PLACEHOLDER_USER:PLACEHOLDER_PASS@cluster0.example.mongodb.net/gaiadetector?retryWrites=true&w=majority")
    MONGODB_DB_NAME: str = Field(default="gaiadetector")

    # JWT Authentication
    JWT_SECRET_KEY: str = Field(default="PLACEHOLDER_CHANGE_THIS_TO_A_STRONG_RANDOM_SECRET")
    JWT_ALGORITHM: str = Field(default="HS256")
    JWT_EXPIRY_MINUTES: int = Field(default=10080)

    # Cookie Security
    COOKIE_SECURE: bool = Field(default=False)
    COOKIE_SAMESITE: str = Field(default="lax")
    COOKIE_NAME: str = Field(default="gaia_access_token")

    # CORS
    CORS_ORIGINS: str = Field(default="http://localhost:5173,http://localhost:3000")

    # Google Drive
    GOOGLE_SERVICE_ACCOUNT_JSON_PATH: str = Field(default="")
    GOOGLE_SERVICE_ACCOUNT_JSON_CONTENT: str = Field(default="")
    GOOGLE_DRIVE_FOLDER_ID: str = Field(default="")

    # Server
    BACKEND_HOST: str = Field(default="0.0.0.0")
    BACKEND_PORT: int = Field(default=8000)
    APP_ENV: str = Field(default="development")
    MAX_UPLOAD_SIZE_MB: int = Field(default=10240)

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def is_mongodb_configured(self) -> bool:
        return bool(self.MONGODB_URI and "PLACEHOLDER" not in self.MONGODB_URI)

    @property
    def is_gdrive_configured(self) -> bool:
        return bool(
            self.GOOGLE_DRIVE_FOLDER_ID
            and "PLACEHOLDER" not in self.GOOGLE_DRIVE_FOLDER_ID
            and (self.GOOGLE_SERVICE_ACCOUNT_JSON_PATH or self.GOOGLE_SERVICE_ACCOUNT_JSON_CONTENT)
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"

settings = Settings()
