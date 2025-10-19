"""
Zenodo Connector
Searches and retrieves research data and publications from Zenodo
"""
import httpx
from loguru import logger
from typing import List, Dict, Any

from medical_discovery.config import settings


class ZenodoConnector:
    """
    Connector for Zenodo API
    
    Provides access to:
    - Research datasets
    - Publications
    - Software
    - Presentations
    """
    
    def __init__(self):
        """Initialize Zenodo connector"""
        self.base_url = settings.zenodo_api_url
        self.token = settings.zenodo_token
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }
        logger.info("Zenodo connector initialized")
    
    async def search(
        self,
        query: str,
        max_results: int = 10,
        resource_type: str = None
    ) -> List[Dict[str, Any]]:
        """
        Search Zenodo for resources
        
        Args:
            query: Search query
            max_results: Maximum number of results
            resource_type: Filter by type ('dataset', 'publication', 'software', etc.)
            
        Returns:
            List of resource metadata dicts
        """
        logger.info(f"Searching Zenodo: {query}")
        
        try:
            params = {
                "q": query,
                "size": max_results,
                "sort": "mostrecent"
            }
            
            if resource_type:
                params["type"] = resource_type
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.base_url}/records",
                    params=params,
                    headers=self.headers
                )
                response.raise_for_status()
                data = response.json()
                
                hits = data.get("hits", {}).get("hits", [])
                logger.info(f"Found {len(hits)} Zenodo resources")
                
                return [self._parse_record(hit) for hit in hits]
                
        except Exception as e:
            logger.exception(f"Zenodo search error: {str(e)}")
            return []
    
    def _parse_record(self, record: Dict[str, Any]) -> Dict[str, Any]:
        """Parse Zenodo record into standard format"""
        metadata = record.get("metadata", {})
        
        title = metadata.get("title", "Untitled")
        description = metadata.get("description", "")
        
        # Extract creators
        creators = metadata.get("creators", [])
        author_names = [c.get("name", "") for c in creators if c.get("name")]
        
        # Build citation
        author_str = ", ".join(author_names[:3])
        if len(author_names) > 3:
            author_str += " et al."
        
        pub_date = metadata.get("publication_date", "Unknown")
        doi = metadata.get("doi", "")
        
        citation = f"{author_str}. {title}. Zenodo. {pub_date}."
        if doi:
            citation += f" DOI: {doi}"
        
        # Get URL
        record_id = record.get("id", "")
        url = f"https://zenodo.org/record/{record_id}" if record_id else ""
        
        # Resource type
        resource_type = metadata.get("resource_type", {}).get("type", "unknown")
        
        # Extract key findings from description
        key_findings = []
        if description:
            # Simple extraction of first few sentences
            sentences = description.split(". ")[:3]
            key_findings = [s.strip() for s in sentences if len(s.strip()) > 20]
        
        return {
            "title": title,
            "description": description[:500],  # Truncate
            "authors": author_names,
            "citation": citation,
            "url": url,
            "doi": doi,
            "resource_type": resource_type,
            "publication_date": pub_date,
            "relevance_score": 0.65,  # Placeholder
            "quality_score": 0.70,     # Placeholder
            "key_findings": key_findings
        }
