"""
KEGG Connector

Provides access to metabolic pathways and molecular interaction networks from KEGG.
KEGG (Kyoto Encyclopedia of Genes and Genomes) is a database resource for understanding
high-level functions and utilities of biological systems.

API Documentation: https://www.kegg.jp/kegg/rest/keggapi.html
"""

import httpx
from typing import List, Dict, Optional, Any
from loguru import logger


class KEGGConnector:
    """
    Connector for KEGG REST API
    
    Searches for pathways, genes, compounds, and diseases.
    No API key required - free academic use.
    """
    
    def __init__(self):
        self.base_url = "https://rest.kegg.jp"
        self.timeout = 30.0
        
    async def search_pathways(
        self,
        query: str,
        organism: str = "hsa"  # hsa = Homo sapiens
    ) -> List[Dict[str, Any]]:
        """
        Search for metabolic pathways
        
        Args:
            query: Search query (pathway name, description)
            organism: KEGG organism code (e.g., "hsa" for human, "mmu" for mouse)
            
        Returns:
            List of pathway records
        """
        try:
            # Get all pathways for organism
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/list/pathway/{organism}"
                )
                response.raise_for_status()
                data = response.text
            
            # Parse response and filter by query
            pathways = []
            query_lower = query.lower()
            
            for line in data.strip().split('\n'):
                if not line:
                    continue
                    
                parts = line.split('\t')
                if len(parts) < 2:
                    continue
                
                pathway_id = parts[0]
                pathway_name = parts[1]
                
                # Filter by query
                if query_lower in pathway_name.lower():
                    pathways.append({
                        "pathway_id": pathway_id,
                        "name": pathway_name,
                        "organism": organism,
                        "url": f"https://www.kegg.jp/pathway/{pathway_id}",
                        "source": "KEGG"
                    })
            
            # Get detailed info for each pathway
            detailed_pathways = []
            for pw in pathways[:20]:  # Limit to avoid too many requests
                details = await self._get_pathway_details(pw["pathway_id"])
                if details:
                    pw.update(details)
                detailed_pathways.append(pw)
            
            logger.info(f"Found {len(detailed_pathways)} pathways in KEGG for query: {query}")
            return detailed_pathways
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error searching KEGG pathways: {str(e)}")
            return []
        except Exception as e:
            logger.exception(f"Error searching KEGG pathways: {str(e)}")
            return []
    
    async def _get_pathway_details(self, pathway_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a pathway
        
        Args:
            pathway_id: KEGG pathway ID (e.g., "hsa05200")
            
        Returns:
            Pathway details
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/get/{pathway_id}"
                )
                response.raise_for_status()
                data = response.text
            
            # Parse KEGG format
            details = {
                "description": "",
                "genes": [],
                "compounds": [],
                "diseases": []
            }
            
            current_section = None
            for line in data.split('\n'):
                if line.startswith('DESCRIPTION'):
                    current_section = 'description'
                    details['description'] = line.replace('DESCRIPTION', '').strip()
                elif line.startswith('GENE'):
                    current_section = 'genes'
                elif line.startswith('COMPOUND'):
                    current_section = 'compounds'
                elif line.startswith('DISEASE'):
                    current_section = 'diseases'
                elif line.startswith(' ') and current_section:
                    # Continuation of previous section
                    if current_section == 'genes':
                        parts = line.strip().split(';')
                        if parts:
                            gene_info = parts[0].strip()
                            if gene_info:
                                details['genes'].append(gene_info)
                    elif current_section == 'compounds':
                        parts = line.strip().split()
                        if len(parts) >= 2:
                            compound_id = parts[0]
                            compound_name = ' '.join(parts[1:])
                            details['compounds'].append({
                                "id": compound_id,
                                "name": compound_name
                            })
            
            return details
            
        except Exception as e:
            logger.error(f"Error getting pathway details for {pathway_id}: {str(e)}")
            return None
    
    async def search_genes(
        self,
        query: str,
        organism: str = "hsa"
    ) -> List[Dict[str, Any]]:
        """
        Search for genes
        
        Args:
            query: Gene name or description
            organism: KEGG organism code
            
        Returns:
            List of gene records
        """
        try:
            # Find genes by keyword
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/find/{organism}/{query}"
                )
                response.raise_for_status()
                data = response.text
            
            genes = []
            for line in data.strip().split('\n'):
                if not line:
                    continue
                
                parts = line.split('\t')
                if len(parts) >= 2:
                    gene_id = parts[0]
                    gene_info = parts[1]
                    
                    # Parse gene info
                    info_parts = gene_info.split(';')
                    gene_name = info_parts[0].strip() if info_parts else ""
                    description = info_parts[1].strip() if len(info_parts) > 1 else ""
                    
                    genes.append({
                        "gene_id": gene_id,
                        "name": gene_name,
                        "description": description,
                        "organism": organism,
                        "url": f"https://www.kegg.jp/entry/{gene_id}",
                        "source": "KEGG"
                    })
            
            logger.info(f"Found {len(genes)} genes in KEGG for query: {query}")
            return genes
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error searching KEGG genes: {str(e)}")
            return []
        except Exception as e:
            logger.exception(f"Error searching KEGG genes: {str(e)}")
            return []
    
    async def search_compounds(
        self,
        query: str
    ) -> List[Dict[str, Any]]:
        """
        Search for chemical compounds
        
        Args:
            query: Compound name or formula
            
        Returns:
            List of compound records
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/find/compound/{query}"
                )
                response.raise_for_status()
                data = response.text
            
            compounds = []
            for line in data.strip().split('\n'):
                if not line:
                    continue
                
                parts = line.split('\t')
                if len(parts) >= 2:
                    compound_id = parts[0]
                    compound_info = parts[1]
                    
                    # Parse compound names (can have multiple names separated by ;)
                    names = compound_info.split(';')
                    primary_name = names[0].strip() if names else ""
                    
                    compounds.append({
                        "compound_id": compound_id,
                        "name": primary_name,
                        "synonyms": [n.strip() for n in names[1:]] if len(names) > 1 else [],
                        "url": f"https://www.kegg.jp/entry/{compound_id}",
                        "source": "KEGG"
                    })
            
            logger.info(f"Found {len(compounds)} compounds in KEGG for query: {query}")
            return compounds
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error searching KEGG compounds: {str(e)}")
            return []
        except Exception as e:
            logger.exception(f"Error searching KEGG compounds: {str(e)}")
            return []
    
    async def search_diseases(
        self,
        query: str
    ) -> List[Dict[str, Any]]:
        """
        Search for diseases
        
        Args:
            query: Disease name or description
            
        Returns:
            List of disease records
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/find/disease/{query}"
                )
                response.raise_for_status()
                data = response.text
            
            diseases = []
            for line in data.strip().split('\n'):
                if not line:
                    continue
                
                parts = line.split('\t')
                if len(parts) >= 2:
                    disease_id = parts[0]
                    disease_name = parts[1]
                    
                    diseases.append({
                        "disease_id": disease_id,
                        "name": disease_name,
                        "url": f"https://www.kegg.jp/entry/{disease_id}",
                        "source": "KEGG"
                    })
            
            logger.info(f"Found {len(diseases)} diseases in KEGG for query: {query}")
            return diseases
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error searching KEGG diseases: {str(e)}")
            return []
        except Exception as e:
            logger.exception(f"Error searching KEGG diseases: {str(e)}")
            return []
