"""
ClinicalTrials.gov Connector

Provides access to clinical trial data from ClinicalTrials.gov using the official API v2.
This is a free, public API that does not require authentication.

API Documentation: https://clinicaltrials.gov/data-api/api
"""

import httpx
from typing import List, Dict, Optional, Any
from loguru import logger

from medical_discovery.utils.epistemic_extractor import extract_epistemic_tags


class ClinicalTrialsConnector:
    """
    Connector for ClinicalTrials.gov API v2
    
    Searches for clinical trials by condition, intervention, or other criteria.
    Returns detailed information about trials including status, phase, outcomes, etc.
    """
    
    def __init__(self):
        self.base_url = "https://clinicaltrials.gov/api/v2"
        self.timeout = 30.0
        
    async def search(
        self,
        query: str,
        condition: Optional[str] = None,
        intervention: Optional[str] = None,
        status: Optional[str] = None,
        phase: Optional[str] = None,
        max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Search clinical trials
        
        Args:
            query: General search query
            condition: Filter by medical condition (e.g., "diabetes", "cancer")
            intervention: Filter by intervention type (e.g., "drug", "behavioral")
            status: Trial status (e.g., "RECRUITING", "COMPLETED", "ACTIVE_NOT_RECRUITING")
            phase: Trial phase (e.g., "PHASE1", "PHASE2", "PHASE3", "PHASE4")
            max_results: Maximum number of results to return
            
        Returns:
            List of clinical trial records with metadata
        """
        try:
            # Build query parameters
            params = {
                "format": "json",
                "pageSize": min(max_results, 100)  # API limit is 100
            }
            
            # Build query filter
            query_parts = []
            if query:
                query_parts.append(query)
            if condition:
                query_parts.append(f"AREA[Condition]{condition}")
            if intervention:
                query_parts.append(f"AREA[InterventionType]{intervention}")
            if status:
                query_parts.append(f"AREA[OverallStatus]{status}")
            if phase:
                query_parts.append(f"AREA[Phase]{phase}")
            
            if query_parts:
                params["query.term"] = " AND ".join(query_parts)
            
            # Make request
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/studies",
                    params=params
                )
                response.raise_for_status()
                data = response.json()
            
            # Parse results
            trials = []
            studies = data.get("studies", [])
            
            for study in studies:
                protocol = study.get("protocolSection", {})
                
                # Extract identification
                identification = protocol.get("identificationModule", {})
                nct_id = identification.get("nctId", "")
                title = identification.get("officialTitle") or identification.get("briefTitle", "")
                
                # Extract status
                status_module = protocol.get("statusModule", {})
                overall_status = status_module.get("overallStatus", "")
                
                # Extract conditions
                conditions_module = protocol.get("conditionsModule", {})
                conditions = conditions_module.get("conditions", [])
                
                # Extract interventions
                interventions_module = protocol.get("armsInterventionsModule", {})
                interventions = []
                for intervention in interventions_module.get("interventions", []):
                    interventions.append({
                        "type": intervention.get("type", ""),
                        "name": intervention.get("name", ""),
                        "description": intervention.get("description", "")
                    })
                
                # Extract design
                design_module = protocol.get("designModule", {})
                phases = design_module.get("phases", [])
                study_type = design_module.get("studyType", "")
                
                # Extract description
                description_module = protocol.get("descriptionModule", {})
                brief_summary = description_module.get("briefSummary", "")
                detailed_description = description_module.get("detailedDescription", "")
                
                # Extract outcomes
                outcomes_module = protocol.get("outcomesModule", {})
                primary_outcomes = []
                for outcome in outcomes_module.get("primaryOutcomes", []):
                    primary_outcomes.append({
                        "measure": outcome.get("measure", ""),
                        "description": outcome.get("description", ""),
                        "timeFrame": outcome.get("timeFrame", "")
                    })
                
                # Extract eligibility
                eligibility_module = protocol.get("eligibilityModule", {})
                eligibility_criteria = eligibility_module.get("eligibilityCriteria", "")
                
                # Extract contacts
                contacts_module = protocol.get("contactsLocationsModule", {})
                locations = []
                for location in contacts_module.get("locations", [])[:5]:  # Limit to 5 locations
                    locations.append({
                        "facility": location.get("facility", ""),
                        "city": location.get("city", ""),
                        "country": location.get("country", "")
                    })
                
                # Extract epistemic metadata
                epistemic_metadata = {}
                try:
                    # Clinical trials are typically RCTs or cohort studies
                    # Phase determines weight: Phase 3/4 > Phase 2 > Phase 1
                    abstract_text = f"{title}. {brief_summary} {detailed_description}"
                    
                    epistemic_metadata = extract_epistemic_tags({
                        "abstract": abstract_text,
                        "title": title,
                        "study_type": "rct" if "INTERVENTIONAL" in study_type.upper() else "cohort",
                        "metadata": {"phases": phases, "nct_id": nct_id}
                    })
                    
                    # Adjust weight by phase
                    if "PHASE3" in phases or "PHASE4" in phases:
                        epistemic_metadata["weight"] = min(epistemic_metadata["weight"] * 1.1, 1.0)
                    elif "PHASE1" in phases or "EARLY_PHASE1" in phases:
                        epistemic_metadata["weight"] = max(epistemic_metadata["weight"] * 0.85, 0.3)
                    
                except Exception as e:
                    logger.debug(f"Epistemic extraction failed for NCT {nct_id}: {str(e)}")
                    epistemic_metadata = {
                        "study_type": "rct",
                        "sample_size": None,
                        "weight": 0.8,  # Default for clinical trials
                        "confidence": 0.6
                    }
                
                trial = {
                    "nct_id": nct_id,
                    "title": title,
                    "url": f"https://clinicaltrials.gov/study/{nct_id}",
                    "status": overall_status,
                    "phases": phases,
                    "study_type": study_type,
                    "conditions": conditions,
                    "interventions": interventions,
                    "brief_summary": brief_summary,
                    "detailed_description": detailed_description,
                    "primary_outcomes": primary_outcomes,
                    "eligibility_criteria": eligibility_criteria,
                    "locations": locations,
                    "source": "ClinicalTrials.gov",
                    "epistemic_metadata": epistemic_metadata
                }
                
                trials.append(trial)
            
            logger.info(f"Found {len(trials)} clinical trials for query: {query}")
            return trials
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error searching ClinicalTrials.gov: {str(e)}")
            return []
        except Exception as e:
            logger.exception(f"Error searching ClinicalTrials.gov: {str(e)}")
            return []
    
    async def get_by_nct_id(self, nct_id: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a specific clinical trial by NCT ID
        
        Args:
            nct_id: ClinicalTrials.gov NCT identifier (e.g., "NCT04368728")
            
        Returns:
            Detailed trial information or None if not found
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/studies/{nct_id}",
                    params={"format": "json"}
                )
                response.raise_for_status()
                data = response.json()
            
            # Parse the study data (similar structure as search results)
            studies = data.get("studies", [])
            if studies:
                # Use the same parsing logic as search()
                results = await self.search(query=nct_id, max_results=1)
                return results[0] if results else None
            
            return None
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error getting trial {nct_id}: {str(e)}")
            return None
        except Exception as e:
            logger.exception(f"Error getting trial {nct_id}: {str(e)}")
            return None
