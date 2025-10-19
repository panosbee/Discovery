"""
Crossref Connector

Provides access to scholarly publication metadata from Crossref.
Crossref is a Digital Object Identifier (DOI) registration agency for scholarly content.

API Documentation: https://api.crossref.org
"""

import httpx
from typing import List, Dict, Optional, Any
from loguru import logger


class CrossrefConnector:
    """
    Connector for Crossref REST API
    
    Searches for publications, retrieves metadata, and finds citations.
    No API key required - free public access (polite mode recommended).
    """
    
    def __init__(self, mailto: Optional[str] = None):
        """
        Initialize Crossref connector
        
        Args:
            mailto: Email address for polite API usage (gets faster response times)
        """
        self.base_url = "https://api.crossref.org"
        self.timeout = 30.0
        self.mailto = mailto or "research@example.com"  # Use polite pool
        
    async def search(
        self,
        query: str,
        filter_params: Optional[Dict[str, str]] = None,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for publications
        
        Args:
            query: Search query
            filter_params: Additional filters (e.g., {"type": "journal-article", "from-pub-date": "2020"})
            max_results: Maximum number of results to return
            
        Returns:
            List of publication records with metadata
        """
        try:
            params = {
                "query": query,
                "rows": min(max_results, 100),  # API limit
                "mailto": self.mailto
            }
            
            # Add filters if provided
            if filter_params:
                filter_str = ",".join([f"{k}:{v}" for k, v in filter_params.items()])
                params["filter"] = filter_str
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/works",
                    params=params
                )
                response.raise_for_status()
                data = response.json()
            
            publications = []
            for item in data.get("message", {}).get("items", []):
                # Extract authors
                authors = []
                for author in item.get("author", []):
                    given = author.get("given", "")
                    family = author.get("family", "")
                    full_name = f"{given} {family}".strip()
                    if full_name:
                        authors.append(full_name)
                
                # Extract publication date
                pub_date_parts = item.get("published-print", {}).get("date-parts", [[]])
                if not pub_date_parts[0]:
                    pub_date_parts = item.get("published-online", {}).get("date-parts", [[]])
                
                pub_year = pub_date_parts[0][0] if pub_date_parts and pub_date_parts[0] else None
                
                # Extract abstract if available
                abstract = item.get("abstract", "")
                
                publication = {
                    "doi": item.get("DOI", ""),
                    "title": item.get("title", [""])[0],
                    "authors": authors,
                    "publisher": item.get("publisher", ""),
                    "container_title": item.get("container-title", [""])[0],  # Journal name
                    "volume": item.get("volume", ""),
                    "issue": item.get("issue", ""),
                    "page": item.get("page", ""),
                    "publication_year": pub_year,
                    "type": item.get("type", ""),
                    "is_referenced_by_count": item.get("is-referenced-by-count", 0),  # Citation count
                    "abstract": abstract,
                    "url": item.get("URL", ""),
                    "source": "Crossref"
                }
                
                publications.append(publication)
            
            logger.info(f"Found {len(publications)} publications in Crossref for query: {query}")
            return publications
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error searching Crossref: {str(e)}")
            return []
        except Exception as e:
            logger.exception(f"Error searching Crossref: {str(e)}")
            return []
    
    async def get_by_doi(self, doi: str) -> Optional[Dict[str, Any]]:
        """
        Get publication details by DOI
        
        Args:
            doi: Digital Object Identifier
            
        Returns:
            Publication metadata or None if not found
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/works/{doi}",
                    params={"mailto": self.mailto}
                )
                response.raise_for_status()
                data = response.json()
            
            item = data.get("message", {})
            
            # Extract authors
            authors = []
            for author in item.get("author", []):
                given = author.get("given", "")
                family = author.get("family", "")
                full_name = f"{given} {family}".strip()
                if full_name:
                    authors.append(full_name)
            
            # Extract publication date
            pub_date_parts = item.get("published-print", {}).get("date-parts", [[]])
            if not pub_date_parts[0]:
                pub_date_parts = item.get("published-online", {}).get("date-parts", [[]])
            
            pub_year = pub_date_parts[0][0] if pub_date_parts and pub_date_parts[0] else None
            
            publication = {
                "doi": item.get("DOI", ""),
                "title": item.get("title", [""])[0],
                "authors": authors,
                "publisher": item.get("publisher", ""),
                "container_title": item.get("container-title", [""])[0],
                "volume": item.get("volume", ""),
                "issue": item.get("issue", ""),
                "page": item.get("page", ""),
                "publication_year": pub_year,
                "type": item.get("type", ""),
                "is_referenced_by_count": item.get("is-referenced-by-count", 0),
                "abstract": item.get("abstract", ""),
                "url": item.get("URL", ""),
                "license": item.get("license", []),
                "references": item.get("reference", []),
                "source": "Crossref"
            }
            
            return publication
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error getting DOI {doi}: {str(e)}")
            return None
        except Exception as e:
            logger.exception(f"Error getting DOI {doi}: {str(e)}")
            return None
    
    async def search_by_field(
        self,
        field: str,
        value: str,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search publications by specific field
        
        Args:
            field: Field name (e.g., "author", "title", "publisher")
            value: Field value to search for
            max_results: Maximum number of results
            
        Returns:
            List of publication records
        """
        try:
            params = {
                f"query.{field}": value,
                "rows": min(max_results, 100),
                "mailto": self.mailto
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/works",
                    params=params
                )
                response.raise_for_status()
                data = response.json()
            
            # Use same parsing as search()
            publications = []
            for item in data.get("message", {}).get("items", []):
                authors = []
                for author in item.get("author", []):
                    given = author.get("given", "")
                    family = author.get("family", "")
                    full_name = f"{given} {family}".strip()
                    if full_name:
                        authors.append(full_name)
                
                pub_date_parts = item.get("published-print", {}).get("date-parts", [[]])
                if not pub_date_parts[0]:
                    pub_date_parts = item.get("published-online", {}).get("date-parts", [[]])
                
                pub_year = pub_date_parts[0][0] if pub_date_parts and pub_date_parts[0] else None
                
                publication = {
                    "doi": item.get("DOI", ""),
                    "title": item.get("title", [""])[0],
                    "authors": authors,
                    "publisher": item.get("publisher", ""),
                    "container_title": item.get("container-title", [""])[0],
                    "publication_year": pub_year,
                    "type": item.get("type", ""),
                    "is_referenced_by_count": item.get("is-referenced-by-count", 0),
                    "url": item.get("URL", ""),
                    "source": "Crossref"
                }
                
                publications.append(publication)
            
            logger.info(f"Found {len(publications)} publications for {field}={value}")
            return publications
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error searching by field: {str(e)}")
            return []
        except Exception as e:
            logger.exception(f"Error searching by field: {str(e)}")
            return []
