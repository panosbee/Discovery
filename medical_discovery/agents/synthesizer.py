"""
Synthesizer Agent
Synthesizes comprehensive hypothesis documents from all gathered information
"""
from loguru import logger
from typing import Dict, Any, List

from medical_discovery.services.deepseek_client import deepseek_client


class SynthesizerAgent:
    """
    Synthesizes all agent outputs into a comprehensive hypothesis document
    
    This agent:
    - Integrates insights from all previous agents
    - Creates a coherent hypothesis narrative
    - Documents mechanism of action
    - Identifies molecular targets and pathways
    - Proposes delivery strategies
    - Lists assumptions and unknowns
    """
    
    def __init__(self):
        """Initialize Synthesizer Agent"""
        logger.info("Synthesizer Agent initialized")
    
    async def synthesize_hypothesis(
        self,
        initial_directions: Dict[str, Any],
        concept_map: Dict[str, Any],
        evidence_packs: List[Dict[str, Any]],
        cross_domain_transfers: List[Dict[str, Any]],
        domain: str,
        goal: str
    ) -> Dict[str, Any]:
        """
        Synthesize comprehensive hypothesis document
        
        Args:
            initial_directions: From Visioner Agent
            concept_map: From Concept Learner
            evidence_packs: From Evidence Miner
            cross_domain_transfers: From Cross-Domain Mapper
            domain: Medical domain
            goal: Research goal
            
        Returns:
            Comprehensive hypothesis document
        """
        logger.info(f"Synthesizing hypothesis for domain: {domain}")
        
        # Prepare context
        directions_text = "\n".join([
            f"- {d.get('title')}: {d.get('mechanism')}"
            for d in initial_directions.get("directions", [])[:3]
        ])
        
        concepts_text = ", ".join([
            c.get("term") for c in concept_map.get("concepts", [])[:10]
        ])
        
        evidence_summary = f"{len(evidence_packs)} evidence sources gathered"
        
        transfers_text = "\n".join([
            f"- {t.get('concept')} from {t.get('source_domain')}"
            for t in cross_domain_transfers[:3]
        ])
        
        system_message = """You are a senior medical researcher specializing in hypothesis development and grant writing.
You excel at synthesizing complex information into coherent, well-structured research hypotheses."""

        prompt = f"""Medical Goal: {goal}
Domain: {domain}

Initial Directions:
{directions_text}

Key Concepts: {concepts_text}

Evidence: {evidence_summary}

Cross-Domain Innovations:
{transfers_text}

Create a comprehensive, publication-ready hypothesis document that includes:

1. **Title**: Clear, descriptive title for the hypothesis
2. **Mechanism of Action**: Detailed description of how the proposed intervention works
3. **Molecular Targets**: Specific molecular targets involved
4. **Pathway Impact**: How this affects relevant biological pathways
5. **Delivery Options**: Proposed methods of delivery/implementation
6. **Expected Outcomes**: Predicted clinical outcomes and benefits
7. **Clinical Rationale**: Why this approach addresses the medical need
8. **Resistance/Relapse Considerations**: For applicable domains
9. **Key Assumptions**: Critical assumptions that need validation
10. **Unknown Factors**: What we don't yet know

Return as JSON:
{{
  "title": "Hypothesis title",
  "mechanism_of_action": "Detailed MOA description",
  "molecular_targets": ["target1", "target2"],
  "pathway_impact": "Description of pathway effects",
  "delivery_options": ["option1", "option2"],
  "expected_outcomes": "Clinical outcomes description",
  "clinical_rationale": "Why this addresses the need",
  "resistance_considerations": "If applicable",
  "key_assumptions": ["assumption1", "assumption2"],
  "unknown_factors": ["unknown1", "unknown2"],
  "validation_plan": "Suggested steps to validate hypothesis"
}}

---

**NOBEL 3.0 LITE: DIVERGENT THINKING MODULE**

After completing the main hypothesis above, generate **2 speculative variants** that explore alternative mechanisms or approaches. These variants should be:
- **Novel** (not obvious from existing literature)
- **Testable** (can be falsified experimentally)
- **Plausible** (grounded in biological/physical principles)

For EACH variant, provide:

**Variant 1 - Cross-Domain Analogy**
Apply concepts from materials science, ecology, systems biology, or other non-medical fields to reframe the problem.
Example: "If biofilm formation uses material reinforcement principles, can we apply polymer degradation strategies from engineering?"

**Variant 2 - Mechanistic Inversion**
Invert a key assumption or mechanism from the main hypothesis.
Example: "Instead of inhibiting protein X, what if we ACTIVATE it with controlled feedback?"

Return variants as JSON array in the SAME response:
{{
  "divergent_variants": [
    {{
      "variant_id": 1,
      "type": "cross_domain_analogy",
      "claim": "Use biofilm dispersal peptides inspired by composite material toughening",
      "source_domain": "materials_science",
      "novelty_justification": "No literature on applying fracture mechanics to EV aggregation",
      "testability": "Can test peptide library against EV clusters in vitro",
      "plausibility_estimate": 0.48
    }},
    {{
      "variant_id": 2,
      "type": "mechanistic_inversion",
      "claim": "Activate L1CAM shedding instead of blocking binding",
      "mechanism_change": "inhibition → controlled activation",
      "novelty_justification": "Current approaches block L1CAM; activation + capture unexplored",
      "testability": "Measure shedding kinetics with agonist compounds",
      "plausibility_estimate": 0.52
    }}
  ]
}}"""

        try:
            result = await deepseek_client.generate_json(
                prompt=prompt,
                system_message=system_message,
                temperature=0.5,
                max_tokens=4000
            )

            # Post-process result: ensure required fields exist and provide sensible fallbacks
            # Some LLM outputs may omit 'abstract' or 'novelty_score' - create safe defaults
            if not result.get("abstract") or result.get("abstract") == "N/A":
                # Build a comprehensive abstract from available data
                title = result.get("title", "Novel therapeutic approach")
                mechanism = result.get("mechanism_of_action", "")
                outcomes = result.get("expected_outcomes", "")
                
                abstract_parts = [
                    f"This hypothesis proposes {title}.",
                ]
                
                if mechanism:
                    abstract_parts.append(f"The approach leverages {mechanism[:150]}...")
                
                if len(cross_domain_transfers) > 0:
                    domains = [t.get("source_domain", "") for t in cross_domain_transfers[:2]]
                    abstract_parts.append(f"Drawing insights from {', '.join(domains)}, this strategy integrates cross-domain innovations.")
                
                if outcomes:
                    abstract_parts.append(f"Expected outcomes include {outcomes[:100]}...")
                
                abstract_parts.append(f"Supported by {len(evidence_packs)} evidence sources including peer-reviewed research and clinical data.")
                
                result["abstract"] = " ".join(abstract_parts)

            if result.get("novelty_score") is None or result.get("novelty_score") == "N/A":
                # Enhanced novelty calculation
                transfers_count = len(cross_domain_transfers or [])
                evidence_count = len(evidence_packs or [])
                
                # Base novelty
                novelty = 0.6
                
                # Bonus for cross-domain transfers (each adds 0.08, max +0.24)
                novelty += min(0.24, transfers_count * 0.08)
                
                # Bonus for fewer evidence packs (more novel = less existing research)
                if evidence_count < 20:
                    novelty += 0.1
                elif evidence_count > 50:
                    novelty -= 0.05
                
                # Cap between 0.5-0.95
                novelty = max(0.5, min(0.95, novelty))
                result["novelty_score"] = round(novelty, 2)

            # Ensure validation_plan exists
            if not result.get("validation_plan"):
                result["validation_plan"] = "Propose in vitro validation, followed by in vivo models and early-phase clinical studies."
            
            # Ensure clinical_rationale exists (REQUIRED by Pydantic schema)
            if not result.get("clinical_rationale"):
                mechanism = result.get("mechanism_of_action", "")
                outcomes = result.get("expected_outcomes", "")
                targets = result.get("molecular_targets", [])
                
                rationale_parts = []
                if mechanism:
                    rationale_parts.append(f"This approach is justified by its {mechanism[:150]}...")
                if targets:
                    rationale_parts.append(f"Targeting {', '.join(targets[:2])} provides a rational therapeutic strategy.")
                if outcomes:
                    rationale_parts.append(f"Expected to achieve {outcomes[:100]}...")
                
                result["clinical_rationale"] = " ".join(rationale_parts) if rationale_parts else "Clinical rationale requires validation through systematic experimental studies."
            
            # Ensure divergent_variants exists (Nobel 3.0 LITE)
            if not result.get("divergent_variants"):
                result["divergent_variants"] = []
                logger.debug("No divergent variants generated by LLM")
            else:
                logger.info(f"Generated {len(result['divergent_variants'])} divergent variants")

            logger.success(f"Synthesized hypothesis: {result.get('title')}")

            return result
            
        except Exception as e:
            logger.exception(f"Error synthesizing hypothesis: {str(e)}")
            
            return {
                "title": f"Novel Therapeutic Approach for {domain}",
                "mechanism_of_action": "Multi-targeted intervention addressing key pathological mechanisms",
                "molecular_targets": ["To be determined"],
                "pathway_impact": "Expected to modulate disease-relevant pathways",
                "delivery_options": ["To be determined"],
                "expected_outcomes": "Improved clinical outcomes",
                "clinical_rationale": "Addresses unmet medical need",
                "resistance_considerations": "To be evaluated",
                "key_assumptions": ["Pathway involvement", "Target accessibility"],
                "unknown_factors": ["Optimal dosing", "Long-term effects"],
                "validation_plan": "Requires further investigation",
                "error": str(e)
            }
