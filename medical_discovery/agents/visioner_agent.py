"""
Visioner Agent
Generates initial hypothesis directions based on goals and constraints
"""
from loguru import logger
from typing import Dict, Any, List, Optional

from medical_discovery.services.deepseek_client import deepseek_client
from medical_discovery.api.schemas.hypothesis import HypothesisConstraints


class VisionerAgent:
    """
    Generates innovative hypothesis directions for medical challenges
    
    This agent:
    - Takes a high-level medical goal
    - Considers domain constraints
    - Generates 2-5 creative hypothesis directions
    - Provides initial mechanistic rationale
    """
    
    def __init__(self):
        """Initialize Visioner Agent"""
        logger.info("Visioner Agent initialized")
    
    async def generate_directions(
        self,
        goal: str,
        domain: str,
        constraints: Optional[HypothesisConstraints] = None
    ) -> Dict[str, Any]:
        """
        Generate initial hypothesis directions
        
        Args:
            goal: The medical challenge or goal
            domain: Medical domain (e.g., 'cardiology', 'diabetes')
            constraints: Optional constraints for hypothesis generation
            
        Returns:
            Dict with hypothesis directions and initial rationale
        """
        logger.info(f"Generating hypothesis directions for: {goal} (domain: {domain})")
        
        # Build constraint description
        constraint_text = ""
        if constraints:
            parts = []
            if constraints.route:
                parts.append(f"Preferred routes: {', '.join([r.value for r in constraints.route])}")
            if constraints.avoid:
                parts.append(f"Avoid: {', '.join(constraints.avoid)}")
            if constraints.focus:
                parts.append(f"Focus areas: {', '.join(constraints.focus)}")
            if constraints.budget_constraints:
                parts.append(f"Budget: {constraints.budget_constraints}")
            if constraints.timeline:
                parts.append(f"Timeline: {constraints.timeline}")
            
            if parts:
                constraint_text = "\n\nConstraints:\n" + "\n".join(f"- {p}" for p in parts)
        
        system_message = """You are an expert medical research strategist and innovator with deep knowledge across all medical domains.
Your role is to generate creative, feasible, and innovative hypothesis directions for medical challenges.

You excel at:
- Cross-domain thinking and transferring ideas between fields
- Identifying novel mechanisms of action
- Considering practical delivery and implementation challenges
- Balancing innovation with clinical feasibility
- Incorporating latest scientific advances

Provide well-reasoned, evidence-aware hypothesis directions."""

        prompt = f"""Medical Challenge:
{goal}

Domain: {domain}{constraint_text}

Please generate 2-5 innovative hypothesis directions to address this medical challenge. For each direction:

1. Provide a clear, concise title
2. Describe the proposed mechanism of action
3. Explain the key innovation or novelty
4. List potential molecular targets or pathways
5. Describe expected therapeutic approach
6. Note any cross-domain inspiration (if applicable)
7. Identify major assumptions that need validation

Return your response as a JSON object with this structure:
{{
  "directions": [
    {{
      "title": "Direction title",
      "mechanism": "Mechanism of action description",
      "innovation": "What makes this novel",
      "targets": ["target1", "target2"],
      "therapeutic_approach": "How this would be delivered/implemented",
      "cross_domain_inspiration": "Optional: inspiration from other fields",
      "assumptions": ["assumption1", "assumption2"]
    }}
  ],
  "domain_context": "Brief context about the domain and current state of the art",
  "selection_rationale": "Why these particular directions were chosen"
}}"""

        try:
            result = await deepseek_client.generate_json(
                prompt=prompt,
                system_message=system_message,
                temperature=0.8,  # Higher temperature for creativity
                max_tokens=3000
            )
            
            logger.success(f"Generated {len(result.get('directions', []))} hypothesis directions")
            logger.debug(f"Directions: {[d.get('title') for d in result.get('directions', [])]}")
            
            return result
            
        except Exception as e:
            logger.exception(f"Error generating hypothesis directions: {str(e)}")
            
            # Return fallback response
            return {
                "directions": [
                    {
                        "title": f"Novel therapeutic approach for {domain}",
                        "mechanism": "Multi-targeted intervention addressing key pathways",
                        "innovation": "Combines existing approaches in novel way",
                        "targets": ["To be determined"],
                        "therapeutic_approach": "To be determined based on further analysis",
                        "cross_domain_inspiration": None,
                        "assumptions": ["Pathway involvement confirmed", "Target accessibility"]
                    }
                ],
                "domain_context": f"Current approaches in {domain} have limitations that need addressing",
                "selection_rationale": "Selected based on clinical need and feasibility",
                "error": str(e)
            }
