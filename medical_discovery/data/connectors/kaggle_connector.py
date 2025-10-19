"""
Kaggle Connector

Provides access to datasets and competitions from Kaggle.
Uses official Kaggle API with credentials from kaggle.json.

API Documentation: https://www.kaggle.com/docs/api
"""

import httpx
import json
import os
from typing import List, Dict, Optional, Any
from loguru import logger
from pathlib import Path


class KaggleConnector:
    """
    Connector for Kaggle API
    
    Searches for datasets and retrieves metadata.
    Requires kaggle.json file with username and key in project root.
    """
    
    def __init__(self, kaggle_config_path: Optional[str] = None):
        """
        Initialize Kaggle connector
        
        Args:
            kaggle_config_path: Path to kaggle.json file (optional, defaults to root/kaggle.json)
        """
        self.base_url = "https://www.kaggle.com/api/v1"
        self.timeout = 30.0
        
        # Load Kaggle credentials
        if kaggle_config_path is None:
            # Try to find kaggle.json in project root
            current_dir = Path(__file__).resolve().parent
            project_root = current_dir.parent.parent.parent
            kaggle_config_path = project_root / "kaggle.json"
        
        self.username = None
        self.key = None
        
        try:
            if os.path.exists(kaggle_config_path):
                with open(kaggle_config_path, 'r') as f:
                    config = json.load(f)
                    self.username = config.get("username")
                    self.key = config.get("key")
                    logger.info(f"Loaded Kaggle credentials for user: {self.username}")
            else:
                logger.warning(f"Kaggle config file not found at: {kaggle_config_path}")
        except Exception as e:
            logger.error(f"Error loading Kaggle credentials: {str(e)}")
    
    def _is_configured(self) -> bool:
        """Check if Kaggle credentials are configured"""
        return self.username is not None and self.key is not None
    
    async def search_datasets(
        self,
        query: str,
        tags: Optional[List[str]] = None,
        file_type: Optional[str] = None,
        sort_by: str = "relevance",
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for datasets on Kaggle
        
        Args:
            query: Search query
            tags: Filter by tags (e.g., ["biology", "medicine", "healthcare"])
            file_type: Filter by file type (e.g., "csv", "json", "sqlite")
            sort_by: Sort order ("hottest", "votes", "updated", "active", "published")
            max_results: Maximum number of results to return
            
        Returns:
            List of dataset records with metadata
        """
        if not self._is_configured():
            logger.error("Kaggle credentials not configured")
            return []
        
        try:
            params = {
                "search": query,
                "sortBy": sort_by,
                "page": 1,
                "maxSize": max_results
            }
            
            if tags:
                params["tagIds"] = ",".join(tags)
            if file_type:
                params["filetype"] = file_type
            
            async with httpx.AsyncClient(
                auth=(self.username, self.key),
                timeout=self.timeout
            ) as client:
                response = await client.get(
                    f"{self.base_url}/datasets/list",
                    params=params
                )
                response.raise_for_status()
                data = response.json()
            
            datasets = []
            for item in data:
                # Extract creator info
                creator_name = item.get("creatorName", "")
                creator_url = item.get("creatorUrl", "")
                
                # Extract dataset info
                dataset_slug = item.get("ref", "")
                title = item.get("title", "")
                subtitle = item.get("subtitle", "")
                description = item.get("description", "")
                
                # Extract statistics
                total_bytes = item.get("totalBytes", 0)
                total_votes = item.get("totalVotes", 0)
                total_views = item.get("totalViews", 0)
                total_downloads = item.get("totalDownloads", 0)
                
                # Extract metadata
                last_updated = item.get("lastUpdated", "")
                license_name = item.get("licenseName", "")
                tags_list = item.get("tags", [])
                
                # Extract file info
                files = item.get("files", [])
                file_count = len(files)
                file_types = list(set([f.get("datasetFileType", "") for f in files if f.get("datasetFileType")]))
                
                dataset = {
                    "dataset_slug": dataset_slug,
                    "title": title,
                    "subtitle": subtitle,
                    "description": description,
                    "creator_name": creator_name,
                    "creator_url": f"https://www.kaggle.com{creator_url}",
                    "size_bytes": total_bytes,
                    "votes": total_votes,
                    "views": total_views,
                    "downloads": total_downloads,
                    "last_updated": last_updated,
                    "license": license_name,
                    "tags": tags_list,
                    "file_count": file_count,
                    "file_types": file_types,
                    "url": f"https://www.kaggle.com/datasets/{dataset_slug}",
                    "source": "Kaggle"
                }
                
                datasets.append(dataset)
            
            logger.info(f"Found {len(datasets)} datasets on Kaggle for query: {query}")
            return datasets
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error searching Kaggle datasets: {str(e)}")
            return []
        except Exception as e:
            logger.exception(f"Error searching Kaggle datasets: {str(e)}")
            return []
    
    async def get_dataset_metadata(
        self,
        owner_slug: str,
        dataset_slug: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get detailed metadata for a specific dataset
        
        Args:
            owner_slug: Dataset owner username
            dataset_slug: Dataset identifier
            
        Returns:
            Dataset metadata or None if not found
        """
        if not self._is_configured():
            logger.error("Kaggle credentials not configured")
            return None
        
        try:
            async with httpx.AsyncClient(
                auth=(self.username, self.key),
                timeout=self.timeout
            ) as client:
                response = await client.get(
                    f"{self.base_url}/datasets/metadata/{owner_slug}/{dataset_slug}"
                )
                response.raise_for_status()
                data = response.json()
            
            metadata = {
                "id": data.get("id"),
                "title": data.get("title", ""),
                "subtitle": data.get("subtitle", ""),
                "description": data.get("description", ""),
                "creator_name": data.get("creatorName", ""),
                "license": data.get("licenseName", ""),
                "keywords": data.get("keywords", []),
                "collaborators": data.get("collaborators", []),
                "data": data.get("data", []),
                "url": f"https://www.kaggle.com/datasets/{owner_slug}/{dataset_slug}",
                "source": "Kaggle"
            }
            
            return metadata
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error getting Kaggle dataset metadata: {str(e)}")
            return None
        except Exception as e:
            logger.exception(f"Error getting Kaggle dataset metadata: {str(e)}")
            return None
    
    async def list_dataset_files(
        self,
        owner_slug: str,
        dataset_slug: str
    ) -> List[Dict[str, Any]]:
        """
        List files in a dataset
        
        Args:
            owner_slug: Dataset owner username
            dataset_slug: Dataset identifier
            
        Returns:
            List of file records
        """
        if not self._is_configured():
            logger.error("Kaggle credentials not configured")
            return []
        
        try:
            async with httpx.AsyncClient(
                auth=(self.username, self.key),
                timeout=self.timeout
            ) as client:
                response = await client.get(
                    f"{self.base_url}/datasets/list/{owner_slug}/{dataset_slug}"
                )
                response.raise_for_status()
                data = response.json()
            
            files = []
            for file_info in data.get("datasetFiles", []):
                files.append({
                    "name": file_info.get("name", ""),
                    "size": file_info.get("totalBytes", 0),
                    "creation_date": file_info.get("creationDate", ""),
                    "description": file_info.get("description", "")
                })
            
            logger.info(f"Found {len(files)} files in dataset {owner_slug}/{dataset_slug}")
            return files
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error listing dataset files: {str(e)}")
            return []
        except Exception as e:
            logger.exception(f"Error listing dataset files: {str(e)}")
            return []
    
    async def search_by_tags(
        self,
        tags: List[str],
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search datasets by specific tags
        
        Args:
            tags: List of tags (e.g., ["amr", "biofilm", "lysins", "biology", "medicine"])
            max_results: Maximum number of results
            
        Returns:
            List of dataset records
        """
        # Convert tags to search query
        query = " ".join(tags)
        return await self.search_datasets(query=query, tags=tags, max_results=max_results)
