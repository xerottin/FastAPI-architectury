
from functools import lru_cache
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from core.config import settings


class MongodbServices:
    @staticmethod
    @lru_cache
    def get_client() -> AsyncIOMotorClient:
        return AsyncIOMotorClient(
            settings.mongo_uri,
            maxPoolSize=50,
            minPoolSize=1,
            serverSelectionTimeoutMS=5000,
            uuidRepresentation="standard",
        )

    @staticmethod
    def get_mongo_db() -> AsyncIOMotorDatabase:
        return MongodbServices.get_client()[settings.mongo_db_name]

    
