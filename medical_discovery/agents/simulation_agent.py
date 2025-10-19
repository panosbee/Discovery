"""
Simulation Agent
Performs in-silico feasibility assessment of hypotheses
"""
from loguru import logger
from typing import Dict, Any
import random

from medical_discovery.services.deepseek_client import deepseek_client


class SimulationAgent:
    """
    Assesses hypothesis feasibility using in-silico models and scoring
    
    This agent:
    - Evaluates therapeutic potential
    - Assesses delivery feasibility
    - Scores safety profile
    - Estimates clinical translatability
    - Provides domain-specific metrics
    """
    
    def __init__(self):
        """Initialize Simulation Agent"""
        logger.info("Simulation Agent initialized")
    
    async def assess_feasibility(
        self,
        hypothesis_document: Dict[str, Any],
        concept_map: Dict[str, Any],
        domain: str
    ) -> Dict[str, Any]:
        """
        Assess hypothesis feasibility
        
        Args:
            hypothesis_document: From Synthesizer
            concept_map: From Concept Learner
            domain: Medical domain
            
        Returns:
            Feasibility scorecard with metrics
        """
        logger.info(f"Assessing feasibility for domain: {domain}")
        
        system_message = """You are an expert in computational biology and drug development with deep knowledge of:
- Pharmacokinetics and pharmacodynamics
- Target druggability
- Delivery systems and bioavailability
- Safety and toxicity prediction
- Clinical trial design and regulatory pathways

Provide realistic, evidence-based feasibility assessments."""

        prompt = f"""Hypothesis: {hypothesis_document.get('title')}

Mechanism: {hypothesis_document.get('mechanism_of_action')}

Targets: {', '.join(hypothesis_document.get('molecular_targets', []))}

Domain: {domain}

Delivery Options: {', '.join(hypothesis_document.get('delivery_options', []))}

Assess the feasibility of this hypothesis across multiple dimensions. Provide scores from 0.0 to 1.0 for:

1. **Therapeutic Potential**: Likelihood of achieving desired therapeutic effect
2. **Delivery Feasibility**: Ease of delivering intervention to target site
3. **Safety Profile**: Expected safety based on mechanism and targets
4. **Clinical Translatability**: Ease of translating to clinical trials

Also provide domain-specific scores relevant to {domain}.

For each score, explain your reasoning and cite key factors.

Return as JSON:
{{
  "therapeutic_potential": 0.75,
  "therapeutic_potential_reasoning": "explanation",
  "delivery_feasibility": 0.65,
  "delivery_feasibility_reasoning": "explanation",
  "safety_profile": 0.80,
  "safety_profile_reasoning": "explanation",
  "clinical_translatability": 0.70,
  "clinical_translatability_reasoning": "explanation",
  "domain_specific_scores": {{
    "metric_name": 0.65
  }},
  "assumptions": ["assumption1", "assumption2"],
  "limitations": ["limitation1", "limitation2"],
  "recommended_validations": ["validation1", "validation2"]
}}"""

        try:
            result = await deepseek_client.generate_json(
                prompt=prompt,
                system_message=system_message,
                temperature=0.3,
                max_tokens=3000
            )
            
            # Ensure scores are within range
            for key in ["therapeutic_potential", "delivery_feasibility", "safety_profile", "clinical_translatability"]:
                if key in result and isinstance(result[key], (int, float)):
                    result[key] = max(0.0, min(1.0, float(result[key])))

            # Provide canonical fields expected by downstream (narrative_generator)
            # technical_feasibility: prefer explicit, else derive from delivery_feasibility or therapeutic_potential
            if "technical_feasibility" in result and isinstance(result.get("technical_feasibility"), (int, float)):
                result["technical_feasibility"] = max(0.0, min(1.0, float(result["technical_feasibility"])))
            else:
                # Derive technical feasibility conservatively
                if "delivery_feasibility" in result and isinstance(result.get("delivery_feasibility"), (int, float)):
                    result["technical_feasibility"] = float(result.get("delivery_feasibility"))
                elif "therapeutic_potential" in result and isinstance(result.get("therapeutic_potential"), (int, float)):
                    result["technical_feasibility"] = float(result.get("therapeutic_potential"))
                else:
                    # fallback to average of available numeric scores
                    nums = [v for k, v in result.items() if k in ("safety_profile", "clinical_translatability") and isinstance(v, (int, float))]
                    result["technical_feasibility"] = (sum(nums) / len(nums)) if nums else 0.5

            # regulatory_path_ready: derive from domain-specific hints or default to moderate
            if "regulatory_path_ready" in result and isinstance(result.get("regulatory_path_ready"), (int, float)):
                result["regulatory_path_ready"] = max(0.0, min(1.0, float(result["regulatory_path_ready"])))
            else:
                # look for explicit domain hints
                ds = result.get("domain_specific_scores", {}) or {}
                reg_hint = None
                for candidate in ["ivd_readiness", "regulatory_ready", "clia_ready"]:
                    if candidate in ds and isinstance(ds[candidate], (int, float)):
                        reg_hint = float(ds[candidate])
                        break
                if reg_hint is not None:
                    result["regulatory_path_ready"] = max(0.0, min(1.0, reg_hint))
                else:
                    # infer from clinical translatability and safety
                    ct = result.get("clinical_translatability", 0.5) if isinstance(result.get("clinical_translatability", None), (int, float)) else 0.5
                    sp = result.get("safety_profile", 0.5) if isinstance(result.get("safety_profile", None), (int, float)) else 0.5
                    result["regulatory_path_ready"] = max(0.01, min(0.99, (ct * 0.6 + sp * 0.4)))
            

            # Ensure main numeric keys exist and are numeric
            for k in ["technical_feasibility", "clinical_translatability", "safety_profile", "regulatory_path_ready"]:
                if k not in result or not isinstance(result.get(k), (int, float)):
                    result[k] = 0.5

            # Compute composite feasibility score (single source of truth)
            # Weighting: technical 35%, clinical 30%, safety 20%, regulatory 15%
            composite = (
                0.35 * float(result.get("technical_feasibility", 0.5)) +
                0.30 * float(result.get("clinical_translatability", 0.5)) +
                0.20 * float(result.get("safety_profile", 0.5)) +
                0.15 * float(result.get("regulatory_path_ready", 0.5))
            )
            
            # Unified labeling rules
            if composite >= 0.70:
                label = "GREEN"
            elif composite >= 0.50:
                label = "AMBER"
            else:
                label = "RED"
            
            # Store composite and label (single source of truth for all downstream)
            result["feasibility_score"] = round(composite, 2)
            result["overall_feasibility"] = label
            
            logger.success(f"Simulation verdict: {label} (composite={composite:.2f})")

            # Ensure domain-specific scores exist
            if "domain_specific_scores" not in result:
                result["domain_specific_scores"] = {}

            return result
            
        except Exception as e:
            logger.exception(f"Error in feasibility assessment: {str(e)}")
            
            # Return conservative baseline scores
            return {
                "therapeutic_potential": 0.6,
                "therapeutic_potential_reasoning": "Requires further validation",
                "delivery_feasibility": 0.6,
                "delivery_feasibility_reasoning": "Standard delivery methods applicable",
                "safety_profile": 0.7,
                "safety_profile_reasoning": "No major safety concerns identified",
                "clinical_translatability": 0.6,
                "clinical_translatability_reasoning": "Standard clinical pathway",
                "domain_specific_scores": {},
                "assumptions": ["Mechanism validity", "Target accessibility"],
                "limitations": ["Limited in-silico data", "Requires experimental validation"],
                "recommended_validations": ["In vitro studies", "Animal models"],
                "error": str(e)
            }
    
    def _avg_score(self, scorecard: Dict[str, Any]) -> float:
        """Calculate average of main scores"""
        scores = []
        for key in ["therapeutic_potential", "delivery_feasibility", "safety_profile", "clinical_translatability"]:
            if key in scorecard and isinstance(scorecard[key], (int, float)):
                scores.append(scorecard[key])
        return sum(scores) / len(scores) if scores else 0.0
