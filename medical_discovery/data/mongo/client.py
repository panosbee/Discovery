"""
MongoDB Database Client
Handles all MongoDB connections and operations
"""
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from loguru import logger
from typing import Optional

from medical_discovery.config import settings


class MongoDBClient:
    """
    Async MongoDB client using Motor
    Provides database connection and collection access
    """
    
    def __init__(self):
        """Initialize MongoDB client"""
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        self._connected = False
    
    async def connect(self):
        """Connect to MongoDB"""
        if self._connected:
            return
        
        try:
            logger.info(f"Connecting to MongoDB at {settings.mongodb_url}")
            
            self.client = AsyncIOMotorClient(
                settings.mongodb_url,
                serverSelectionTimeoutMS=5000,
                maxPoolSize=50,
                minPoolSize=10
            )
            
            # Test connection
            await self.client.admin.command('ping')
            
            self.db = self.client[settings.mongodb_database]
            self._connected = True
            
            logger.success(f"Connected to MongoDB database: {settings.mongodb_database}")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            self._connected = False
            logger.info("Disconnected from MongoDB")
    
    def get_collection(self, collection_name: str):
        """Get a collection from the database"""
        if not self._connected or self.db is None:
            raise RuntimeError("MongoDB not connected. Call connect() first.")
        return self.db[collection_name]
    
    async def is_connected(self) -> bool:
        """Check if MongoDB is connected"""
        if self.client is None:
            return False
        
        try:
            await self.client.admin.command('ping')
            return True
        except Exception:
            return False


# Global MongoDB client instance
mongodb_client = MongoDBClient()
