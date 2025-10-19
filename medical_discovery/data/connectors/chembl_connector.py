"""
ChEMBL Connector

Provides access to bioactivity data from ChEMBL database.
ChEMBL is a manually curated database of bioactive molecules with drug-like properties.

API Documentation: https://chembl.gitbook.io/chembl-interface-documentation/web-services
"""

import httpx
from typing import List, Dict, Optional, Any
from loguru import logger


class ChEMBLConnector:
    """
    Connector for ChEMBL REST API
    
    Searches for bioactive molecules, targets, assays, and drug data.
    No API key required - free public access.
    """
    
    def __init__(self):
        self.base_url = "https://www.ebi.ac.uk/chembl/api/data"
        self.timeout = 30.0
        
    async def search_molecules(
        self,
        query: str,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for molecules by name or identifier
        
        Args:
            query: Search query (molecule name, ChEMBL ID, synonyms)
            max_results: Maximum number of results to return
            
        Returns:
            List of molecule records with bioactivity data
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/molecule/search.json",
                    params={
                        "q": query,
                        "limit": max_results
                    }
                )
                response.raise_for_status()
                data = response.json()
            
            molecules = []
            for mol in data.get("molecules", []):
                # Skip if mol is None or empty
                if not mol:
                    continue
                    
                molecule = {
                    "chembl_id": mol.get("molecule_chembl_id", ""),
                    "pref_name": mol.get("pref_name", ""),
                    "molecule_type": mol.get("molecule_type", ""),
                    "max_phase": mol.get("max_phase"),  # Clinical development phase (0-4)
                    "first_approval": mol.get("first_approval"),
                    "oral": mol.get("oral"),
                    "parenteral": mol.get("parenteral"),
                    "topical": mol.get("topical"),
                    "black_box_warning": mol.get("black_box_warning"),
                    "natural_product": mol.get("natural_product"),
                    "first_in_class": mol.get("first_in_class"),
                    "chirality": mol.get("chirality"),
                    "prodrug": mol.get("prodrug"),
                    "therapeutic_flag": mol.get("therapeutic_flag"),
                    "molecular_weight": (mol.get("molecule_properties") or {}).get("full_mwt"),
                    "alogp": (mol.get("molecule_properties") or {}).get("alogp"),
                    "hba": (mol.get("molecule_properties") or {}).get("hba"),  # H-bond acceptors
                    "hbd": (mol.get("molecule_properties") or {}).get("hbd"),  # H-bond donors
                    "psa": (mol.get("molecule_properties") or {}).get("psa"),  # Polar surface area
                    "rtb": (mol.get("molecule_properties") or {}).get("rtb"),  # Rotatable bonds
                    "ro3_pass": (mol.get("molecule_properties") or {}).get("ro3_pass"),  # Rule of 3
                    "num_ro5_violations": (mol.get("molecule_properties") or {}).get("num_ro5_violations"),  # Lipinski's rule
                    "canonical_smiles": (mol.get("molecule_structures") or {}).get("canonical_smiles", ""),
                    "standard_inchi": (mol.get("molecule_structures") or {}).get("standard_inchi", ""),
                    "standard_inchi_key": (mol.get("molecule_structures") or {}).get("standard_inchi_key", ""),
                    "url": f"https://www.ebi.ac.uk/chembl/compound_report_card/{mol.get('molecule_chembl_id', '')}",
                    "source": "ChEMBL"
                }
                molecules.append(molecule)
            
            logger.info(f"Found {len(molecules)} molecules in ChEMBL for query: {query}")
            return molecules
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error searching ChEMBL molecules: {str(e)}")
            return []
        except Exception as e:
            logger.exception(f"Error searching ChEMBL molecules: {str(e)}")
            return []
    
    async def search_targets(
        self,
        query: str,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for biological targets (proteins, organisms, etc.)
        
        Args:
            query: Search query (target name, UniProt ID, gene name)
            max_results: Maximum number of results to return
            
        Returns:
            List of target records
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/target/search.json",
                    params={
                        "q": query,
                        "limit": max_results
                    }
                )
                response.raise_for_status()
                data = response.json()
            
            targets = []
            for tgt in data.get("targets", []):
                target = {
                    "chembl_id": tgt.get("target_chembl_id", ""),
                    "pref_name": tgt.get("pref_name", ""),
                    "target_type": tgt.get("target_type", ""),
                    "organism": tgt.get("organism", ""),
                    "tax_id": tgt.get("tax_id"),
                    "gene_names": tgt.get("target_components", [{}])[0].get("target_component_synonyms", []) if tgt.get("target_components") else [],
                    "url": f"https://www.ebi.ac.uk/chembl/target_report_card/{tgt.get('target_chembl_id', '')}",
                    "source": "ChEMBL"
                }
                targets.append(target)
            
            logger.info(f"Found {len(targets)} targets in ChEMBL for query: {query}")
            return targets
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error searching ChEMBL targets: {str(e)}")
            return []
        except Exception as e:
            logger.exception(f"Error searching ChEMBL targets: {str(e)}")
            return []
    
    async def get_bioactivities(
        self,
        molecule_chembl_id: str,
        max_results: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get bioactivity data for a specific molecule
        
        Args:
            molecule_chembl_id: ChEMBL molecule ID (e.g., "CHEMBL25")
            max_results: Maximum number of results to return
            
        Returns:
            List of bioactivity records
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/activity.json",
                    params={
                        "molecule_chembl_id": molecule_chembl_id,
                        "limit": max_results
                    }
                )
                response.raise_for_status()
                data = response.json()
            
            activities = []
            for act in data.get("activities", []):
                activity = {
                    "activity_id": act.get("activity_id"),
                    "assay_chembl_id": act.get("assay_chembl_id", ""),
                    "assay_description": act.get("assay_description", ""),
                    "assay_type": act.get("assay_type", ""),
                    "standard_type": act.get("standard_type", ""),  # e.g., IC50, Ki, EC50
                    "standard_relation": act.get("standard_relation", ""),
                    "standard_value": act.get("standard_value"),
                    "standard_units": act.get("standard_units", ""),
                    "pchembl_value": act.get("pchembl_value"),  # -log(molar IC50, XC50, EC50, AC50, Ki, Kd or Potency)
                    "target_chembl_id": act.get("target_chembl_id", ""),
                    "target_pref_name": act.get("target_pref_name", ""),
                    "target_organism": act.get("target_organism", ""),
                    "document_chembl_id": act.get("document_chembl_id", ""),
                    "source": "ChEMBL"
                }
                activities.append(activity)
            
            logger.info(f"Found {len(activities)} bioactivities for {molecule_chembl_id}")
            return activities
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error getting bioactivities: {str(e)}")
            return []
        except Exception as e:
            logger.exception(f"Error getting bioactivities: {str(e)}")
            return []
    
    async def search_drugs(
        self,
        query: str,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search for approved drugs
        
        Args:
            query: Search query (drug name, indication, etc.)
            max_results: Maximum number of results to return
            
        Returns:
            List of approved drug records
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/drug.json",
                    params={
                        "search": query,
                        "limit": max_results
                    }
                )
                response.raise_for_status()
                data = response.json()
            
            drugs = []
            for drug in data.get("drugs", []):
                drug_record = {
                    "molecule_chembl_id": drug.get("molecule_chembl_id", ""),
                    "pref_name": drug.get("pref_name", ""),
                    "synonyms": drug.get("synonyms", []),
                    "max_phase": drug.get("max_phase"),
                    "first_approval": drug.get("first_approval"),
                    "indication_class": drug.get("indication_class", ""),
                    "drug_type": drug.get("drug_type", ""),
                    "availability_type": drug.get("availability_type", ""),
                    "applicants": drug.get("applicants", []),
                    "url": f"https://www.ebi.ac.uk/chembl/compound_report_card/{drug.get('molecule_chembl_id', '')}",
                    "source": "ChEMBL"
                }
                drugs.append(drug_record)
            
            logger.info(f"Found {len(drugs)} drugs in ChEMBL for query: {query}")
            return drugs
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error searching ChEMBL drugs: {str(e)}")
            return []
        except Exception as e:
            logger.exception(f"Error searching ChEMBL drugs: {str(e)}")
            return []
