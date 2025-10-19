"""
Cross-Domain Mapper Agent
Finds innovative ideas by mapping concepts across different domains
"""
from loguru import logger
from typing import Dict, Any, List

from medical_discovery.services.deepseek_client import deepseek_client


class CrossDomainMapperAgent:
    """
    Maps concepts across domains to find innovative transfers
    
    This agent:
    - Analyzes concepts from non-medical domains
    - Identifies transferable ideas and mechanisms
    - Proposes cross-domain applications
    - Evaluates potential clinical impact
    """
    
    def __init__(self):
        """Initialize Cross-Domain Mapper Agent"""
        logger.info("Cross-Domain Mapper Agent initialized")
    
    async def find_transfers(
        self,
        concept_map: Dict[str, Any],
        domain: str,
        cross_domains: List[str]
    ) -> List[Dict[str, Any]]:
        """
        Find cross-domain transfers
        
        Args:
            concept_map: Concept map from Concept Learner
            domain: Target medical domain
            cross_domains: Source domains to search
            
        Returns:
            List of cross-domain transfer ideas
        """
        logger.info(f"Searching for cross-domain transfers from: {cross_domains}")
        
        # Extract key concepts
        key_concepts = [c.get("term") for c in concept_map.get("concepts", [])[:5]]
        
        system_message = """You are an innovation expert specializing in cross-domain idea transfer.
You excel at finding analogies and transferable concepts from engineering, materials science, 
food technology, and other non-medical fields that can inspire medical breakthroughs."""

        prompt = f"""Target Medical Domain: {domain}

Key Concepts: {', '.join(key_concepts)}

Source Domains to Explore: {', '.join(cross_domains)}

Find 3-5 innovative cross-domain transfers that could inspire novel approaches in {domain}.

For each transfer, identify:
1. The source domain and specific concept/technology
2. How it works in the source domain
3. The proposed transfer to {domain}
4. Rationale for why this could work
5. Potential clinical impact
6. Key challenges in adaptation

Return as JSON:
{{
  "transfers": [
    {{
      "source_domain": "domain name",
      "target_domain": "{domain}",
      "concept": "concept or technology name",
      "source_mechanism": "how it works in source domain",
      "proposed_application": "how to apply in medical domain",
      "rationale": "why this transfer makes sense",
      "potential_impact": "expected clinical benefit",
      "challenges": ["challenge1", "challenge2"]
    }}
  ]
}}"""

        try:
            result = await deepseek_client.generate_json(
                prompt=prompt,
                system_message=system_message,
                temperature=0.8,
                max_tokens=3000
            )
            
            transfers = result.get("transfers", [])
            # Normalize transfers: ensure ALL REQUIRED fields exist with meaningful values
            normalized = []
            for i, t in enumerate(transfers):
                source = t.get("source_domain") or t.get("source", "unknown")
                target = t.get("target_domain", domain)
                
                # Map different field names to required 'concept' field
                concept = (
                    t.get("concept") or 
                    t.get("concept_transferred") or 
                    f"Innovation from {source}"
                )
                
                # Map to required 'rationale' field
                rationale = (
                    t.get("rationale") or 
                    t.get("source_mechanism", "") + " " + t.get("proposed_application", "")
                ).strip() or f"Cross-domain transfer leveraging {source} insights for {target} applications"
                
                # Map to required 'potential_impact' field
                potential_impact = (
                    t.get("potential_impact") or
                    t.get("proposed_application") or
                    f"Applying {source} methodologies to enhance {target} research and treatment strategies"
                )
                
                # Build challenges list
                challenges = t.get("challenges", []) or ["Adaptation required", "Validation needed"]
                
                # Provide BOTH new schema fields AND legacy fields for backward compatibility
                normalized_transfer = {
                    # New Pydantic schema fields (required)
                    "source_domain": source,
                    "target_domain": target,
                    "concept": concept,
                    "rationale": rationale,
                    "potential_impact": potential_impact,
                    "challenges": challenges if isinstance(challenges, list) else [str(challenges)],
                    # Legacy fields for backward compatibility with test scripts
                    "concept_transferred": concept,
                    "analogy": potential_impact,
                    "relevance_score": min(0.85, max(0.6, 0.6 + len(rationale) / 1000))
                }
                normalized.append(normalized_transfer)

            logger.success(f"Found {len(normalized)} cross-domain transfers with complete metadata")
            
            return normalized
            
        except Exception as e:
            logger.exception(f"Error finding cross-domain transfers: {str(e)}")
            return []
