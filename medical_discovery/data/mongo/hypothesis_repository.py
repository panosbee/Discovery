"""
Hypothesis Repository
Handles all database operations for hypotheses
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from loguru import logger

from medical_discovery.data.mongo.client import mongodb_client
from medical_discovery.api.schemas.hypothesis import (
    HypothesisResponse,
    HypothesisStatus,
    MedicalDomain
)


class HypothesisRepository:
    """
    Repository pattern for hypothesis data access
    Provides CRUD operations for hypotheses in MongoDB
    """
    
    COLLECTION_NAME = "hypotheses"
    
    def __init__(self):
        """Initialize repository"""
        self.collection = None
    
    async def _ensure_collection(self):
        """Ensure collection is available"""
        if self.collection is None:
            self.collection = mongodb_client.get_collection(self.COLLECTION_NAME)
    
    async def create(self, hypothesis_data: Dict[str, Any]) -> str:
        """
        Create a new hypothesis
        
        Args:
            hypothesis_data: Hypothesis data dict
            
        Returns:
            Hypothesis ID
        """
        await self._ensure_collection()
        
        try:
            # Add timestamps
            now = datetime.utcnow()
            hypothesis_data["created_at"] = now
            hypothesis_data["updated_at"] = now
            
            result = await self.collection.insert_one(hypothesis_data)
            
            logger.info(f"Created hypothesis {hypothesis_data['id']} in MongoDB")
            
            return hypothesis_data["id"]
            
        except Exception as e:
            logger.exception(f"Error creating hypothesis in MongoDB: {str(e)}")
            raise
    
    async def get_by_id(self, hypothesis_id: str) -> Optional[Dict[str, Any]]:
        """
        Get hypothesis by ID
        
        Args:
            hypothesis_id: Hypothesis ID
            
        Returns:
            Hypothesis data or None if not found
        """
        await self._ensure_collection()
        
        try:
            result = await self.collection.find_one({"id": hypothesis_id})
            
            if result:
                # Remove MongoDB _id field
                result.pop("_id", None)
                logger.debug(f"Retrieved hypothesis {hypothesis_id} from MongoDB")
            
            return result
            
        except Exception as e:
            logger.exception(f"Error retrieving hypothesis {hypothesis_id}: {str(e)}")
            raise
    
    async def update(self, hypothesis_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Update hypothesis
        
        Args:
            hypothesis_id: Hypothesis ID
            update_data: Fields to update
            
        Returns:
            True if updated, False if not found
        """
        await self._ensure_collection()
        
        try:
            # Add updated timestamp
            update_data["updated_at"] = datetime.utcnow()
            
            result = await self.collection.update_one(
                {"id": hypothesis_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                logger.info(f"Updated hypothesis {hypothesis_id} in MongoDB")
                return True
            
            return False
            
        except Exception as e:
            logger.exception(f"Error updating hypothesis {hypothesis_id}: {str(e)}")
            raise
    
    async def delete(self, hypothesis_id: str) -> bool:
        """
        Delete hypothesis
        
        Args:
            hypothesis_id: Hypothesis ID
            
        Returns:
            True if deleted, False if not found
        """
        await self._ensure_collection()
        
        try:
            result = await self.collection.delete_one({"id": hypothesis_id})
            
            if result.deleted_count > 0:
                logger.info(f"Deleted hypothesis {hypothesis_id} from MongoDB")
                return True
            
            return False
            
        except Exception as e:
            logger.exception(f"Error deleting hypothesis {hypothesis_id}: {str(e)}")
            raise
    
    async def list(
        self,
        status: Optional[HypothesisStatus] = None,
        domain: Optional[MedicalDomain] = None,
        user_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List hypotheses with filters
        
        Args:
            status: Filter by status
            domain: Filter by domain
            user_id: Filter by user ID
            limit: Maximum results
            offset: Skip this many results
            
        Returns:
            List of hypothesis dicts
        """
        await self._ensure_collection()
        
        try:
            # Build query
            query = {}
            
            if status:
                query["status"] = status.value
            
            if domain:
                query["domain"] = domain.value
            
            if user_id:
                query["user_id"] = user_id
            
            # Execute query with pagination
            cursor = self.collection.find(query)
            cursor.sort("created_at", -1)  # Sort by newest first
            cursor.skip(offset).limit(limit)
            
            results = []
            async for doc in cursor:
                doc.pop("_id", None)  # Remove MongoDB _id
                results.append(doc)
            
            logger.info(f"Listed {len(results)} hypotheses from MongoDB")
            
            return results
            
        except Exception as e:
            logger.exception(f"Error listing hypotheses: {str(e)}")
            raise
    
    async def count(
        self,
        status: Optional[HypothesisStatus] = None,
        domain: Optional[MedicalDomain] = None,
        user_id: Optional[str] = None
    ) -> int:
        """
        Count hypotheses with filters
        
        Args:
            status: Filter by status
            domain: Filter by domain
            user_id: Filter by user ID
            
        Returns:
            Count of matching hypotheses
        """
        await self._ensure_collection()
        
        try:
            # Build query
            query = {}
            
            if status:
                query["status"] = status.value
            
            if domain:
                query["domain"] = domain.value
            
            if user_id:
                query["user_id"] = user_id
            
            count = await self.collection.count_documents(query)
            
            return count
            
        except Exception as e:
            logger.exception(f"Error counting hypotheses: {str(e)}")
            raise


# Global repository instance
hypothesis_repository = HypothesisRepository()
