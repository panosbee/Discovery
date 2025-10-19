"""
arXiv Connector

Provides access to scientific preprints from arXiv.org.
arXiv is a free distribution service and open-access archive for scholarly articles.

API Documentation: https://arxiv.org/help/api
"""

import httpx
from typing import List, Dict, Optional, Any
from loguru import logger
import xml.etree.ElementTree as ET


class ArxivConnector:
    """
    Connector for arXiv API
    
    Searches for preprints and retrieves metadata.
    No API key required - free public access.
    """
    
    def __init__(self):
        self.base_url = "https://export.arxiv.org/api/query"
        self.timeout = 30.0
        
    async def search(
        self,
        query: str,
        category: Optional[str] = None,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for preprints on arXiv
        
        Args:
            query: Search query
            category: arXiv category (e.g., "q-bio" for quantitative biology, "physics.med-ph" for medical physics)
            max_results: Maximum number of results to return
            
        Returns:
            List of preprint records with metadata
        """
        try:
            # Build search query
            search_query = query
            if category:
                search_query = f"cat:{category} AND {query}"
            
            params = {
                "search_query": search_query,
                "start": 0,
                "max_results": max_results,
                "sortBy": "relevance",
                "sortOrder": "descending"
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    self.base_url,
                    params=params
                )
                response.raise_for_status()
                
            # Parse XML response
            root = ET.fromstring(response.content)
            
            # Define namespace
            ns = {
                'atom': 'http://www.w3.org/2005/Atom',
                'arxiv': 'http://arxiv.org/schemas/atom'
            }
            
            preprints = []
            for entry in root.findall('atom:entry', ns):
                # Extract basic info
                arxiv_id = entry.find('atom:id', ns).text.split('/')[-1] if entry.find('atom:id', ns) is not None else ""
                title = entry.find('atom:title', ns).text.strip() if entry.find('atom:title', ns) is not None else ""
                summary = entry.find('atom:summary', ns).text.strip() if entry.find('atom:summary', ns) is not None else ""
                published = entry.find('atom:published', ns).text if entry.find('atom:published', ns) is not None else ""
                updated = entry.find('atom:updated', ns).text if entry.find('atom:updated', ns) is not None else ""
                
                # Extract authors
                authors = []
                for author in entry.findall('atom:author', ns):
                    name = author.find('atom:name', ns)
                    if name is not None:
                        authors.append(name.text)
                
                # Extract categories
                categories = []
                for cat in entry.findall('atom:category', ns):
                    term = cat.get('term')
                    if term:
                        categories.append(term)
                
                # Extract PDF link
                pdf_link = ""
                for link in entry.findall('atom:link', ns):
                    if link.get('title') == 'pdf':
                        pdf_link = link.get('href', "")
                        break
                
                # Extract DOI if available
                doi = ""
                doi_elem = entry.find('arxiv:doi', ns)
                if doi_elem is not None:
                    doi = doi_elem.text
                
                # Extract comment
                comment = ""
                comment_elem = entry.find('arxiv:comment', ns)
                if comment_elem is not None:
                    comment = comment_elem.text
                
                preprint = {
                    "arxiv_id": arxiv_id,
                    "title": title,
                    "authors": authors,
                    "summary": summary,
                    "published": published[:10],  # Extract date only (YYYY-MM-DD)
                    "updated": updated[:10],
                    "categories": categories,
                    "doi": doi,
                    "comment": comment,
                    "pdf_url": pdf_link,
                    "url": f"https://arxiv.org/abs/{arxiv_id}",
                    "source": "arXiv"
                }
                
                preprints.append(preprint)
            
            logger.info(f"Found {len(preprints)} preprints on arXiv for query: {query}")
            return preprints
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error searching arXiv: {str(e)}")
            return []
        except Exception as e:
            logger.exception(f"Error searching arXiv: {str(e)}")
            return []
    
    async def get_by_id(self, arxiv_id: str) -> Optional[Dict[str, Any]]:
        """
        Get preprint details by arXiv ID
        
        Args:
            arxiv_id: arXiv identifier (e.g., "2103.12345" or "physics.med-ph/0703131")
            
        Returns:
            Preprint metadata or None if not found
        """
        try:
            params = {
                "id_list": arxiv_id,
                "max_results": 1
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    self.base_url,
                    params=params
                )
                response.raise_for_status()
            
            # Parse XML response
            root = ET.fromstring(response.content)
            
            ns = {
                'atom': 'http://www.w3.org/2005/Atom',
                'arxiv': 'http://arxiv.org/schemas/atom'
            }
            
            entry = root.find('atom:entry', ns)
            if entry is None:
                return None
            
            # Extract all information (similar to search method)
            arxiv_id = entry.find('atom:id', ns).text.split('/')[-1] if entry.find('atom:id', ns) is not None else ""
            title = entry.find('atom:title', ns).text.strip() if entry.find('atom:title', ns) is not None else ""
            summary = entry.find('atom:summary', ns).text.strip() if entry.find('atom:summary', ns) is not None else ""
            published = entry.find('atom:published', ns).text if entry.find('atom:published', ns) is not None else ""
            updated = entry.find('atom:updated', ns).text if entry.find('atom:updated', ns) is not None else ""
            
            authors = []
            for author in entry.findall('atom:author', ns):
                name = author.find('atom:name', ns)
                if name is not None:
                    authors.append(name.text)
            
            categories = []
            for cat in entry.findall('atom:category', ns):
                term = cat.get('term')
                if term:
                    categories.append(term)
            
            pdf_link = ""
            for link in entry.findall('atom:link', ns):
                if link.get('title') == 'pdf':
                    pdf_link = link.get('href', "")
                    break
            
            doi = ""
            doi_elem = entry.find('arxiv:doi', ns)
            if doi_elem is not None:
                doi = doi_elem.text
            
            preprint = {
                "arxiv_id": arxiv_id,
                "title": title,
                "authors": authors,
                "summary": summary,
                "published": published[:10],
                "updated": updated[:10],
                "categories": categories,
                "doi": doi,
                "pdf_url": pdf_link,
                "url": f"https://arxiv.org/abs/{arxiv_id}",
                "source": "arXiv"
            }
            
            return preprint
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error getting arXiv ID {arxiv_id}: {str(e)}")
            return None
        except Exception as e:
            logger.exception(f"Error getting arXiv ID {arxiv_id}: {str(e)}")
            return None
