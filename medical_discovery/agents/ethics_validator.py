"""
Ethics Validator Agent
Validates hypotheses for ethical, safety, and regulatory compliance
"""
from loguru import logger
from typing import Dict, Any, Optional

from medical_discovery.services.deepseek_client import deepseek_client
from medical_discovery.api.schemas.hypothesis import HypothesisConstraints


class EthicsValidatorAgent:
    """
    Validates hypotheses for ethics, safety, and clinical feasibility
    
    This agent:
    - Assesses safety concerns
    - Identifies regulatory requirements
    - Evaluates ethical implications
    - Considers vulnerable populations
    - Recommends safeguards
    - Provides Green/Amber/Red verdict
    """
    
    def __init__(self):
        """Initialize Ethics Validator Agent"""
        logger.info("Ethics Validator Agent initialized")
    
    async def validate(
        self,
        hypothesis_document: Dict[str, Any],
        simulation_scorecard: Dict[str, Any],
        domain: str,
        constraints: Optional[HypothesisConstraints] = None
    ) -> Dict[str, Any]:
        """
        Validate hypothesis for ethics and safety
        
        Args:
            hypothesis_document: From Synthesizer
            simulation_scorecard: From Simulation Agent
            domain: Medical domain
            constraints: Optional constraints
            
        Returns:
            Ethics validation report with verdict
        """
        logger.info(f"Validating ethics for domain: {domain}")
        
        safety_score = simulation_scorecard.get("safety_profile", 0.5)
        
        system_message = """You are a medical ethics and regulatory expert with expertise in:
- Clinical research ethics (Declaration of Helsinki, Belmont Report)
- Regulatory frameworks (FDA, EMA, ICH-GCP)
- Patient safety and informed consent
- Risk-benefit analysis
- Healthcare equity and access
- Special populations (pediatrics, pregnancy, elderly)

Provide thorough, balanced ethical assessments."""

        prompt = f"""Hypothesis: {hypothesis_document.get('title')}

Mechanism: {hypothesis_document.get('mechanism_of_action')}

Domain: {domain}

Safety Profile Score: {safety_score}

Expected Outcomes: {hypothesis_document.get('expected_outcomes')}

Delivery: {', '.join(hypothesis_document.get('delivery_options', []))}

Conduct a comprehensive ethical and regulatory assessment. Consider:

1. **Safety Concerns**: Potential risks to patients
2. **Regulatory Path**: FDA/EMA requirements, clinical trial phases
3. **Ethical Flags**: Special ethical considerations
4. **Vulnerable Populations**: Groups requiring special protection
5. **Informed Consent**: Considerations for consent process
6. **Equity**: Access and cost-effectiveness
7. **Domain-Specific Ethics**: Ethics specific to {domain}

Provide a verdict:
- **GREEN**: Ethically sound, no major concerns
- **AMBER**: Acceptable with safeguards and monitoring
- **RED**: Significant ethical/safety concerns requiring resolution

---

**NOBEL 3.0 LITE: RED-TEAM ADVERSARIAL REVIEW**

Before assigning the final verdict, conduct a **critical adversarial analysis** to identify fragile assumptions:

**Red-Team Questions:**
1. What are the TOP 3 **fragile assumptions** in this hypothesis? (Assumptions that, if wrong, would invalidate the approach)
2. What **potential confounders** could explain the expected outcomes without the proposed mechanism?
3. What **alternative explanations** exist for the same clinical problem that might be simpler/safer?

**Verdict Override Rule:**
- If you identify >2 **critical fragilities** (assumptions with no fallback plan) → max verdict = AMBER
- Document fragile assumptions even for GREEN verdicts (for transparency)

Return as JSON:
{{
  "verdict": "green|amber|red",
  "verdict_reasoning": "explanation of verdict",
  "safety_concerns": ["concern1", "concern2"],
  "regulatory_considerations": ["requirement1", "requirement2"],
  "ethical_flags": ["flag1", "flag2"],
  "vulnerable_populations": ["population1", "population2"],
  "informed_consent_considerations": ["consideration1", "consideration2"],
  "recommended_safeguards": ["safeguard1", "safeguard2"],
  "cost_effectiveness": "assessment of accessibility and affordability",
  "domain_specific_ethics": "ethics considerations specific to domain",
  "preclinical_requirements": ["requirement1", "requirement2"],
  "clinical_trial_design_notes": "key considerations for trial design",
  "fragile_assumptions": [
    {{"assumption": "L1CAM antibody specificity", "impact_if_wrong": "False positives from other adhesion molecules", "mitigation": "Orthogonal EV markers (CD9/CD63)"}},
    {{"assumption": "PBMC batch effects are negligible", "impact_if_wrong": "Noise overwhelms signal", "mitigation": "Batch correction + reference materials"}}
  ],
  "potential_confounders": ["Hemolysis", "Platelet activation", "Sample storage conditions"],
  "alternative_explanations": ["Simpler biomarker approaches", "Imaging-based diagnostics"]
}}"""

        try:
            result = await deepseek_client.generate_json(
                prompt=prompt,
                system_message=system_message,
                temperature=0.3,
                max_tokens=3000
            )
            
            verdict = result.get("verdict", "amber").lower()
            logger.success(f"Ethics validation complete. Verdict: {verdict.upper()}")
            
            # Ensure verdict is valid
            if verdict not in ["green", "amber", "red"]:
                result["verdict"] = "amber"
            
            # RED-TEAM OVERRIDE: If >2 critical fragilities, downgrade to AMBER
            fragile_assumptions = result.get("fragile_assumptions", [])
            if len(fragile_assumptions) > 2 and verdict == "green":
                logger.warning(f"Downgrading verdict from GREEN to AMBER due to {len(fragile_assumptions)} fragile assumptions")
                result["verdict"] = "amber"
                result["verdict_reasoning"] += f" [DOWNGRADED: {len(fragile_assumptions)} critical fragilities identified]"
            
            # Ensure fragile_assumptions exists (for narrative)
            if "fragile_assumptions" not in result:
                result["fragile_assumptions"] = []
            
            # Ensure confounders/alternatives exist
            if "potential_confounders" not in result:
                result["potential_confounders"] = []
            if "alternative_explanations" not in result:
                result["alternative_explanations"] = []
            
            logger.info(f"Identified {len(fragile_assumptions)} fragile assumptions, "
                       f"{len(result.get('potential_confounders', []))} confounders")
            
            return result
            
        except Exception as e:
            logger.exception(f"Error in ethics validation: {str(e)}")
            
            # Return conservative amber verdict
            return {
                "verdict": "amber",
                "verdict_reasoning": "Requires standard ethical review and monitoring",
                "safety_concerns": ["Requires safety monitoring", "Long-term effects unknown"],
                "regulatory_considerations": [
                    "FDA IND application required",
                    "Phase I-III clinical trials needed",
                    "Good Clinical Practice (GCP) compliance"
                ],
                "ethical_flags": ["Standard informed consent required"],
                "vulnerable_populations": ["To be determined based on indication"],
                "informed_consent_considerations": ["Risks and benefits disclosure", "Alternative treatments"],
                "recommended_safeguards": [
                    "Safety monitoring committee",
                    "Regular adverse event reporting",
                    "Patient follow-up protocol"
                ],
                "cost_effectiveness": "To be evaluated",
                "domain_specific_ethics": f"Standard ethics for {domain} research apply",
                "preclinical_requirements": ["In vitro studies", "Animal models", "Toxicology studies"],
                "clinical_trial_design_notes": "Standard randomized controlled trial design recommended",
                "error": str(e)
            }
