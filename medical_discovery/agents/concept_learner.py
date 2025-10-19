"""
Concept Learner Agent
Builds comprehensive concept maps with definitions, relationships, and pathways
"""
import asyncio
from loguru import logger
from typing import Dict, Any, List

from medical_discovery.services.deepseek_client import deepseek_client


class ConceptLearnerAgent:
    """
    Builds domain-specific concept maps for hypothesis development
    
    This agent:
    - Extracts key concepts from goals and initial directions
    - Provides detailed definitions for each concept
    - Maps relationships between concepts
    - Identifies relevant pathways and molecular targets
    - Creates a prerequisite tree for downstream agents
    """
    
    def __init__(self):
        """Initialize Concept Learner Agent"""
        logger.info("Concept Learner Agent initialized")
    
    async def build_concept_map(
        self,
        goal: str,
        domain: str,
        initial_directions: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Build a comprehensive concept map
        
        Args:
            goal: The medical goal
            domain: Medical domain
            initial_directions: Output from Visioner Agent
            
        Returns:
            Concept map with definitions, relationships, and pathways
        """
        logger.info(f"Building concept map for domain: {domain}")
        
        # Extract key terms from directions
        directions_summary = "\n".join([
            f"- {d.get('title')}: {d.get('mechanism')}"
            for d in initial_directions.get('directions', [])
        ])
        
        system_message = """You are an expert medical knowledge engineer specializing in creating comprehensive concept maps for medical research.

Your expertise includes:
- Medical terminology and ontologies (MeSH, UMLS, ICD)
- Biological pathways and molecular mechanisms
- Drug-target interactions
- Disease pathophysiology
- Clinical manifestations and biomarkers

Create detailed, accurate concept maps that serve as knowledge foundations for hypothesis development."""

        prompt = f"""Medical Goal: {goal}

Domain: {domain}

Initial Hypothesis Directions:
{directions_summary}

Create a comprehensive concept map for this medical challenge. Extract and define all key concepts, including:
- Disease mechanisms
- Molecular targets
- Biological pathways
- Potential interventions
- Biomarkers
- Clinical outcomes
- Relevant cell types/tissues

For each concept, provide:
1. Clear definition
2. Related medical terms (synonyms, related concepts)
3. Relevant biological pathways
4. Known molecular targets
5. Clinical significance

Also map the relationships between concepts (e.g., "insulin resistance" → "decreased glucose uptake" → "hyperglycemia").

Return as JSON:
{{
  "concepts": [
    {{
      "term": "concept name",
      "definition": "detailed definition",
      "related_terms": ["term1", "term2"],
      "pathways": ["pathway1", "pathway2"],
      "targets": ["target1", "target2"],
      "clinical_significance": "why this matters clinically"
    }}
  ],
  "relationships": {{
    "concept1": ["related_concept1", "related_concept2"],
    "concept2": ["related_concept3"]
  }},
  "key_pathways": [
    {{
      "name": "pathway name",
      "description": "what this pathway does",
      "relevance": "why relevant to the goal"
    }}
  ],
  "glossary": {{
    "term1": "definition",
    "term2": "definition"
  }}
}}"""

        # Retry logic for malformed JSON responses
        max_retries = 3
        last_error = None
        result = None
        
        try:
            for attempt in range(max_retries):
                try:
                    result = await deepseek_client.generate_json(
                        prompt=prompt,
                        system_message=system_message,
                        temperature=0.3,  # Lower temperature for accuracy
                        max_tokens=4000
                    )
                    
                    # Validate response structure
                    if not isinstance(result, dict):
                        raise ValueError(f"Expected dict, got {type(result)}")
                    if "concepts" not in result or not isinstance(result["concepts"], list):
                        raise ValueError("Missing or invalid 'concepts' field")
                    
                    logger.success(f"Built concept map with {len(result.get('concepts', []))} concepts")
                    logger.debug(f"Key pathways: {[p.get('name') for p in result.get('key_pathways', [])]}")
                    
                    break  # Success, exit retry loop
                    
                except (ValueError, KeyError, TypeError) as e:
                    last_error = e
                    logger.warning(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
                    if attempt < max_retries - 1:
                        logger.info(f"Retrying concept map generation...")
                        await asyncio.sleep(2)  # Brief delay before retry
                    else:
                        logger.error(f"All {max_retries} attempts failed. Using fallback.")
                        raise  # Re-raise to trigger outer exception handler
            
            # Post-process: ensure device/wearable concepts are present when relevant
            if result:
                text_context = f"{goal} {directions_summary}".lower()
                wearable_keywords = ["wear", "wearable", "sensor", "ecg", "wearables", "device", "sensor data"]
                if any(k in text_context for k in wearable_keywords):
                    # If no wearable-related concept exists, inject one
                    existing_terms = [c.get("term", "").lower() for c in result.get("concepts", [])]
                    if not any("wear" in t or "sensor" in t or "ecg" in t or "device" in t for t in existing_terms):
                        wearable_concept = {
                            "term": "wearable sensors",
                            "definition": "Non-invasive wearable devices that capture physiological signals (e.g., ECG, PPG, accelerometry)",
                            "related_terms": ["ECG", "PPG", "accelerometer", "biosensor"],
                            "pathways": [],
                            "targets": [],
                            "clinical_significance": "Enables continuous monitoring and early detection of physiological anomalies"
                        }
                        result.setdefault("concepts", []).insert(0, wearable_concept)
            
            return result
            
        except Exception as e:
            logger.exception(f"Error building concept map: {str(e)}")
            
            # Return minimal concept map
            return {
                "concepts": [
                    {
                        "term": domain,
                        "definition": f"Medical concepts related to {domain}",
                        "related_terms": [],
                        "pathways": [],
                        "targets": [],
                        "clinical_significance": "Core to the medical challenge"
                    }
                ],
                "relationships": {},
        "key_pathways": [],
                "glossary": {},
                "error": str(e)
            }
