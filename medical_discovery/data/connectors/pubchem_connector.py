"""
PubChem Connector

Provides access to chemical compound data from PubChem.
PubChem is a free, public database of chemical structures and biological activities.

API Documentation: https://pubchemdocs.ncbi.nlm.nih.gov/pug-rest
"""

import httpx
from typing import List, Dict, Optional, Any
from loguru import logger
import asyncio


class PubChemConnector:
    """
    Connector for PubChem PUG REST API
    
    Searches for chemical compounds, retrieves properties, bioassays, and related data.
    No API key required - free public access.
    """
    
    def __init__(self):
        self.base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
        self.timeout = 30.0
        
    async def search_compounds(
        self,
        query: str,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for chemical compounds by name, formula, or identifier
        
        Args:
            query: Search query (compound name, formula, SMILES, InChI, etc.)
            max_results: Maximum number of results to return
            
        Returns:
            List of compound records with properties
        """
        try:
            # First, get CIDs (Compound IDs) matching the query
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/compound/name/{query}/cids/JSON"
                )
                
                if response.status_code == 404:
                    logger.info(f"No compounds found for query: {query}")
                    return []
                
                response.raise_for_status()
                data = response.json()
            
            cids = data.get("IdentifierList", {}).get("CID", [])[:max_results]
            
            if not cids:
                return []
            
            # Get detailed properties for each compound
            compounds = []
            for cid in cids:
                compound_data = await self._get_compound_details(cid)
                if compound_data:
                    compounds.append(compound_data)
            
            logger.info(f"Found {len(compounds)} compounds for query: {query}")
            return compounds
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error searching PubChem: {str(e)}")
            return []
        except Exception as e:
            logger.exception(f"Error searching PubChem: {str(e)}")
            return []
    
    async def _get_compound_details(self, cid: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed properties for a specific compound
        
        Args:
            cid: PubChem Compound ID (CID)
            
        Returns:
            Compound details or None if not found
        """
        try:
            # Get compound properties
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/compound/cid/{cid}/property/"
                    "MolecularFormula,MolecularWeight,CanonicalSMILES,"
                    "IsomericSMILES,InChI,InChIKey,IUPACName,XLogP,"
                    "ExactMass,MonoisotopicMass,TPSA,Complexity,"
                    "Charge,HBondDonorCount,HBondAcceptorCount,"
                    "RotatableBondCount,HeavyAtomCount/JSON"
                )
                response.raise_for_status()
                properties = response.json()
            
            props = properties.get("PropertyTable", {}).get("Properties", [{}])[0]
            
            compound = {
                "cid": cid,
                "url": f"https://pubchem.ncbi.nlm.nih.gov/compound/{cid}",
                "molecular_formula": props.get("MolecularFormula", ""),
                "molecular_weight": props.get("MolecularWeight", 0),
                "iupac_name": props.get("IUPACName", ""),
                "canonical_smiles": props.get("CanonicalSMILES", ""),
                "isomeric_smiles": props.get("IsomericSMILES", ""),
                "inchi": props.get("InChI", ""),
                "inchi_key": props.get("InChIKey", ""),
                "xlogp": props.get("XLogP"),
                "exact_mass": props.get("ExactMass"),
                "tpsa": props.get("TPSA"),  # Topological Polar Surface Area
                "complexity": props.get("Complexity"),
                "charge": props.get("Charge", 0),
                "h_bond_donor_count": props.get("HBondDonorCount", 0),
                "h_bond_acceptor_count": props.get("HBondAcceptorCount", 0),
                "rotatable_bond_count": props.get("RotatableBondCount", 0),
                "heavy_atom_count": props.get("HeavyAtomCount", 0),
                "source": "PubChem"
            }
            
            return compound
            
        except Exception as e:
            logger.error(f"Error getting compound details for CID {cid}: {str(e)}")
            return None
    
    async def search_bioassays(
        self,
        query: str,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for biological assays related to a query
        
        Args:
            query: Search query (compound name, disease, protein, etc.)
            max_results: Maximum number of results to return
            
        Returns:
            List of bioassay records
        """
        try:
            # Search for assay IDs
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/assay/name/{query}/aids/JSON"
                )
                
                if response.status_code == 404:
                    logger.info(f"No bioassays found for query: {query}")
                    return []
                
                response.raise_for_status()
                data = response.json()
            
            aids = data.get("IdentifierList", {}).get("AID", [])[:max_results]
            
            if not aids:
                return []
            
            # Get details for each assay
            assays = []
            for aid in aids:
                assay_data = await self._get_assay_details(aid)
                if assay_data:
                    assays.append(assay_data)
            
            logger.info(f"Found {len(assays)} bioassays for query: {query}")
            return assays
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error searching bioassays: {str(e)}")
            return []
        except Exception as e:
            logger.exception(f"Error searching bioassays: {str(e)}")
            return []
    
    async def _get_assay_details(self, aid: int) -> Optional[Dict[str, Any]]:
        """
        Get details for a specific bioassay
        
        Args:
            aid: PubChem Assay ID (AID)
            
        Returns:
            Assay details or None if not found
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/assay/aid/{aid}/description/JSON"
                )
                response.raise_for_status()
                data = response.json()
            
            desc = data.get("PC_AssayContainer", [{}])[0].get("assay", {}).get("descr", {})
            
            assay = {
                "aid": aid,
                "url": f"https://pubchem.ncbi.nlm.nih.gov/bioassay/{aid}",
                "name": desc.get("name", ""),
                "description": desc.get("description", [{}])[0].get("description", "") if desc.get("description") else "",
                "protocol": desc.get("protocol", [{}])[0].get("protocol", "") if desc.get("protocol") else "",
                "target": desc.get("target", [{}])[0] if desc.get("target") else {},
                "activity_outcome_method": desc.get("activity_outcome_method", ""),
                "source": "PubChem BioAssay"
            }
            
            return assay
            
        except Exception as e:
            logger.error(f"Error getting assay details for AID {aid}: {str(e)}")
            return None
    
    async def get_compound_by_cid(self, cid: int) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific compound by CID
        
        Args:
            cid: PubChem Compound ID
            
        Returns:
            Compound details or None if not found
        """
        return await self._get_compound_details(cid)
