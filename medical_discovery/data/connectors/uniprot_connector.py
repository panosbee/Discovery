"""
UniProt Connector

Provides access to protein sequence and functional information from UniProt.
UniProt is a comprehensive resource for protein sequence and annotation data.

API Documentation: https://www.uniprot.org/help/api
"""

import httpx
from typing import List, Dict, Optional, Any
from loguru import logger


class UniProtConnector:
    """
    Connector for UniProt REST API
    
    Searches for proteins, retrieves sequences, annotations, and functional data.
    No API key required - free public access.
    """
    
    def __init__(self):
        self.base_url = "https://rest.uniprot.org/uniprotkb"
        self.timeout = 30.0
        
    async def search(
        self,
        query: str,
        organism: Optional[str] = None,
        reviewed: Optional[bool] = None,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for proteins
        
        Args:
            query: Search query (protein name, gene name, function, etc.)
            organism: Organism name or taxonomy ID (e.g., "human", "9606")
            reviewed: Filter by review status (True for Swiss-Prot, False for TrEMBL)
            max_results: Maximum number of results to return
            
        Returns:
            List of protein records with annotations
        """
        try:
            # Build query
            search_query = query
            if organism:
                search_query += f" AND organism:{organism}"
            if reviewed is not None:
                search_query += f" AND reviewed:{'true' if reviewed else 'false'}"
            
            params = {
                "query": search_query,
                "format": "json",
                "size": min(max_results, 500)  # API limit
            }
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/search",
                    params=params
                )
                response.raise_for_status()
                data = response.json()
            
            proteins = []
            for result in data.get("results", []):
                # Extract primary accession
                primary_accession = result.get("primaryAccession", "")
                
                # Extract protein names
                protein_description = result.get("proteinDescription", {})
                recommended_name = protein_description.get("recommendedName", {})
                protein_name = recommended_name.get("fullName", {}).get("value", "")
                
                # Extract gene names
                genes = result.get("genes", [])
                gene_names = []
                if genes:
                    primary_gene = genes[0].get("geneName", {})
                    gene_name_value = primary_gene.get("value", "")
                    if gene_name_value:
                        gene_names.append(gene_name_value)
                
                # Extract organism
                organism_info = result.get("organism", {})
                organism_name = organism_info.get("scientificName", "")
                tax_id = organism_info.get("taxonId", 0)
                
                # Extract sequence info
                sequence = result.get("sequence", {})
                sequence_length = sequence.get("length", 0)
                sequence_mass = sequence.get("molWeight", 0)
                
                # Extract comments (function, pathway, etc.)
                comments = result.get("comments", [])
                function_text = ""
                pathway_text = ""
                for comment in comments:
                    if comment.get("commentType") == "FUNCTION":
                        texts = comment.get("texts", [])
                        if texts:
                            function_text = texts[0].get("value", "")
                    elif comment.get("commentType") == "PATHWAY":
                        texts = comment.get("texts", [])
                        if texts:
                            pathway_text = texts[0].get("value", "")
                
                # Extract cross-references
                cross_refs = result.get("uniProtKBCrossReferences", [])
                pdb_ids = []
                for ref in cross_refs:
                    if ref.get("database") == "PDB":
                        pdb_ids.append(ref.get("id", ""))
                
                # Extract keywords
                keywords = result.get("keywords", [])
                keyword_names = [kw.get("name", "") for kw in keywords]
                
                protein = {
                    "accession": primary_accession,
                    "protein_name": protein_name,
                    "gene_names": gene_names,
                    "organism": organism_name,
                    "taxonomy_id": tax_id,
                    "reviewed": result.get("entryType") == "UniProtKB reviewed (Swiss-Prot)",
                    "sequence_length": sequence_length,
                    "sequence_mass": sequence_mass,
                    "function": function_text,
                    "pathway": pathway_text,
                    "pdb_ids": pdb_ids[:5],  # Limit to 5 PDB structures
                    "keywords": keyword_names[:10],  # Limit to 10 keywords
                    "url": f"https://www.uniprot.org/uniprotkb/{primary_accession}",
                    "source": "UniProt"
                }
                
                proteins.append(protein)
            
            logger.info(f"Found {len(proteins)} proteins in UniProt for query: {query}")
            return proteins
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error searching UniProt: {str(e)}")
            return []
        except Exception as e:
            logger.exception(f"Error searching UniProt: {str(e)}")
            return []
    
    async def get_by_accession(self, accession: str) -> Optional[Dict[str, Any]]:
        """
        Get protein details by UniProt accession number
        
        Args:
            accession: UniProt accession (e.g., "P12345")
            
        Returns:
            Protein details or None if not found
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/{accession}.json"
                )
                response.raise_for_status()
                result = response.json()
            
            # Extract information (similar to search method)
            primary_accession = result.get("primaryAccession", "")
            
            protein_description = result.get("proteinDescription", {})
            recommended_name = protein_description.get("recommendedName", {})
            protein_name = recommended_name.get("fullName", {}).get("value", "")
            
            genes = result.get("genes", [])
            gene_names = []
            if genes:
                primary_gene = genes[0].get("geneName", {})
                gene_name_value = primary_gene.get("value", "")
                if gene_name_value:
                    gene_names.append(gene_name_value)
            
            organism_info = result.get("organism", {})
            organism_name = organism_info.get("scientificName", "")
            tax_id = organism_info.get("taxonId", 0)
            
            sequence = result.get("sequence", {})
            sequence_length = sequence.get("length", 0)
            sequence_value = sequence.get("value", "")
            
            comments = result.get("comments", [])
            function_text = ""
            for comment in comments:
                if comment.get("commentType") == "FUNCTION":
                    texts = comment.get("texts", [])
                    if texts:
                        function_text = texts[0].get("value", "")
                        break
            
            protein = {
                "accession": primary_accession,
                "protein_name": protein_name,
                "gene_names": gene_names,
                "organism": organism_name,
                "taxonomy_id": tax_id,
                "reviewed": result.get("entryType") == "UniProtKB reviewed (Swiss-Prot)",
                "sequence_length": sequence_length,
                "sequence": sequence_value,
                "function": function_text,
                "url": f"https://www.uniprot.org/uniprotkb/{primary_accession}",
                "source": "UniProt"
            }
            
            return protein
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error getting UniProt accession {accession}: {str(e)}")
            return None
        except Exception as e:
            logger.exception(f"Error getting UniProt accession {accession}: {str(e)}")
            return None
    
    async def search_by_gene(
        self,
        gene_name: str,
        organism: str = "human",
        max_results: int = 10
    ) -> List[Dict[str, Any]]:
        """
        Search for proteins by gene name
        
        Args:
            gene_name: Gene name (e.g., "TP53", "BRCA1")
            organism: Organism name
            max_results: Maximum number of results
            
        Returns:
            List of protein records
        """
        query = f"gene:{gene_name}"
        return await self.search(query=query, organism=organism, max_results=max_results)
