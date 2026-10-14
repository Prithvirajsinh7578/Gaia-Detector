import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import pymongo
from app.core.config import settings

logger = logging.getLogger(__name__)

class DatabaseManager:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None

    async def connect(self) -> None:
        if not settings.is_mongodb_configured:
            logger.warning("MongoDB URI is not configured or using placeholders. Database connection skipped.")
            return

        try:
            self.client = AsyncIOMotorClient(
                settings.MONGODB_URI,
                serverSelectionTimeoutMS=5000
            )
            self.db = self.client[settings.MONGODB_DB_NAME]
            logger.info("Connected to MongoDB Atlas client.")
            await self.ensure_indexes()
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB client: {e}")
            self.client = None
            self.db = None

    async def ensure_indexes(self) -> None:
        """Create required unique and query indexes on startup."""
        if self.db is None:
            return
        try:
            # Users: unique normalized email
            await self.db.users.create_index(
                [("email", pymongo.ASCENDING)],
                unique=True,
                name="idx_users_email_unique"
            )
            # Detections: user_id + created_at compound index for fast history queries
            await self.db.detections.create_index(
                [("user_id", pymongo.ASCENDING), ("created_at", pymongo.DESCENDING)],
                name="idx_detections_user_created"
            )
            # Uploads: user_id + created_at
            await self.db.uploads.create_index(
                [("user_id", pymongo.ASCENDING), ("created_at", pymongo.DESCENDING)],
                name="idx_uploads_user_created"
            )
            logger.info("MongoDB indexes verified/created successfully.")
        except Exception as e:
            logger.warning(f"Could not create MongoDB indexes: {e}")

    def close(self) -> None:
        if self.client:
            self.client.close()
            logger.info("MongoDB connection closed.")
            self.client = None
            self.db = None

    async def ping(self) -> bool:
        if not self.client:
            return False
        try:
            await self.client.admin.command("ping")
            return True
        except Exception as e:
            logger.warning(f"MongoDB ping failed: {e}")
            return False

db_manager = DatabaseManager()

def get_database() -> Optional[AsyncIOMotorDatabase]:
    return db_manager.db
