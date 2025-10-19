"""
PubMed Connector
Searches and retrieves medical literature from PubMed
"""
import httpx
from loguru import logger
from typing import List, Dict, Any, Optional
from xml.etree import ElementTree as ET

from medical_discovery.config import settings
from medical_discovery.utils.epistemic_extractor import extract_epistemic_tags


class PubMedConnector:
    """
    Connector for PubMed/NCBI E-utilities API
    
    Provides access to:
    - PubMed literature search
    - Article metadata retrieval
    - Citation extraction
    - Abstract text
    """
    
    def __init__(self):
        """Initialize PubMed connector"""
        self.base_url = settings.pubmed_api_url
        self.api_key = settings.pubmed_api_key
        self.email = settings.pubmed_email
        self.tool = settings.pubmed_tool
        logger.info("PubMed connector initialized")
    
    async def search(
        self,
        query: str,
        max_results: int = 20,
        sort: str = "relevance"
    ) -> List[Dict[str, Any]]:
        """
        Search PubMed for articles
        
        Args:
            query: Search query
            max_results: Maximum number of results
            sort: Sort order ('relevance' or 'pub_date')
            
        Returns:
            List of article metadata dicts
        """
        logger.info(f"Searching PubMed: {query}")
        
        try:
            # Step 1: Search for PMIDs
            pmids = await self._esearch(query, max_results, sort)
            
            if not pmids:
                logger.warning("No PubMed results found")
                return []
            
            logger.info(f"Found {len(pmids)} PubMed articles")
            
            # Step 2: Fetch article details
            articles = await self._efetch(pmids)
            
            return articles
            
        except Exception as e:
            logger.exception(f"PubMed search error: {str(e)}")
            return []
    
    async def _esearch(
        self,
        query: str,
        max_results: int,
        sort: str
    ) -> List[str]:
        """Execute ESearch to get PMIDs"""
        params = {
            "db": "pubmed",
            "term": query,
            "retmax": max_results,
            "retmode": "json",
            "sort": sort,
            "api_key": self.api_key,
            "tool": self.tool,
            "email": self.email
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/esearch.fcgi",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            return data.get("esearchresult", {}).get("idlist", [])
    
    async def _efetch(self, pmids: List[str]) -> List[Dict[str, Any]]:
        """Fetch article details using EFetch"""
        if not pmids:
            return []
        
        params = {
            "db": "pubmed",
            "id": ",".join(pmids),
            "retmode": "xml",
            "api_key": self.api_key,
            "tool": self.tool,
            "email": self.email
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{self.base_url}/efetch.fcgi",
                params=params
            )
            response.raise_for_status()
            
            # Parse XML
            return self._parse_pubmed_xml(response.text)
    
    def _parse_pubmed_xml(self, xml_text: str) -> List[Dict[str, Any]]:
        """Parse PubMed XML response"""
        articles = []
        
        try:
            root = ET.fromstring(xml_text)
            
            for article_elem in root.findall(".//PubmedArticle"):
                try:
                    article = self._extract_article_data(article_elem)
                    articles.append(article)
                except Exception as e:
                    logger.debug(f"Error parsing article: {str(e)}")
                    continue
            
        except Exception as e:
            logger.error(f"Error parsing PubMed XML: {str(e)}")
        
        return articles
    
    def _extract_article_data(self, article_elem: ET.Element) -> Dict[str, Any]:
        """Extract data from a single article element"""
        # PMID
        pmid_elem = article_elem.find(".//PMID")
        pmid = pmid_elem.text if pmid_elem is not None else "Unknown"
        
        # Title
        title_elem = article_elem.find(".//ArticleTitle")
        title = title_elem.text if title_elem is not None else "No title"
        
        # Abstract
        abstract_parts = []
        for abstract_text in article_elem.findall(".//AbstractText"):
            if abstract_text.text:
                abstract_parts.append(abstract_text.text)
        abstract = " ".join(abstract_parts) if abstract_parts else ""
        
        # Authors
        authors = []
        for author_elem in article_elem.findall(".//Author"):
            lastname = author_elem.find("LastName")
            forename = author_elem.find("ForeName")
            if lastname is not None:
                name = lastname.text
                if forename is not None:
                    name = f"{forename.text} {name}"
                authors.append(name)
        
        # Journal
        journal_elem = article_elem.find(".//Journal/Title")
        journal = journal_elem.text if journal_elem is not None else "Unknown Journal"
        
        # Year
        year_elem = article_elem.find(".//PubDate/Year")
        year = year_elem.text if year_elem is not None else "Unknown"
        
        # Build citation
        author_str = ", ".join(authors[:3])
        if len(authors) > 3:
            author_str += " et al."
        citation = f"{author_str}. {title}. {journal}. {year}."
        
        # Extract key findings from abstract (simple sentence extraction)
        key_findings = []
        if abstract:
            sentences = abstract.split(". ")
            # Take sentences containing key terms
            key_terms = ["found", "showed", "demonstrated", "revealed", "indicated", "suggests", "associated"]
            for sentence in sentences[:5]:  # First 5 sentences
                if any(term in sentence.lower() for term in key_terms):
                    key_findings.append(sentence.strip())
        
        # Extract epistemic metadata
        epistemic_metadata = {}
        try:
            epistemic_metadata = extract_epistemic_tags({
                "abstract": abstract,
                "title": title,
                "publication_type": "",  # PubMed XML has MeSH types, could extract
                "metadata": {}
            })
        except Exception as e:
            logger.debug(f"Epistemic extraction failed for PMID {pmid}: {str(e)}")
            epistemic_metadata = {
                "study_type": "unknown",
                "sample_size": None,
                "weight": 0.4,
                "confidence": 0.0
            }
        
        return {
            "pmid": pmid,
            "title": title,
            "abstract": abstract,
            "authors": authors,
            "journal": journal,
            "year": year,
            "citation": citation,
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            "relevance_score": 0.75,  # Placeholder
            "quality_score": 0.80,     # Placeholder
            "key_findings": key_findings[:3],  # Top 3
            "excerpts": [abstract[:500]] if abstract else [],
            "epistemic_metadata": epistemic_metadata
        }
