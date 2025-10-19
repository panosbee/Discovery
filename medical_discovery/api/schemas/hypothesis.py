"""
Pydantic schemas for hypothesis generation API
Defines request/response models for the Medical Discovery Engine
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


class MedicalDomain(str, Enum):
    """Supported medical domains"""
    CARDIOLOGY = "cardiology"
    ONCOLOGY = "oncology"
    NEUROLOGY = "neurology"
    DIABETES = "diabetes"
    INFECTIOUS_DISEASES = "infectious_diseases"
    GENETICS = "genetics"
    IMMUNOLOGY = "immunology"
    NEPHROLOGY = "nephrology"
    PULMONOLOGY = "pulmonology"
    GASTROENTEROLOGY = "gastroenterology"
    ENDOCRINOLOGY = "endocrinology"
    HEMATOLOGY = "hematology"
    RHEUMATOLOGY = "rheumatology"
    PSYCHIATRY = "psychiatry"
    GENERAL_MEDICINE = "general_medicine"


class HypothesisStatus(str, Enum):
    """Hypothesis generation status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class FeasibilityLevel(str, Enum):
    """Feasibility assessment levels"""
    GREEN = "green"
    AMBER = "amber"
    RED = "red"


class RouteOfAdministration(str, Enum):
    """Routes of drug/intervention administration"""
    ORAL = "oral"
    TOPICAL = "topical"
    LOCALIZED = "localized"
    SYSTEMIC = "systemic"
    INTRAVENOUS = "intravenous"
    SUBCUTANEOUS = "subcutaneous"
    INTRAMUSCULAR = "intramuscular"
    INHALATION = "inhalation"
    TRANSDERMAL = "transdermal"


class HypothesisConstraints(BaseModel):
    """Constraints for hypothesis generation"""
    route: Optional[List[RouteOfAdministration]] = Field(
        default=None,
        description="Preferred routes of administration"
    )
    avoid: Optional[List[str]] = Field(
        default=None,
        description="Specific toxicities, mechanisms, or approaches to avoid"
    )
    focus: Optional[List[str]] = Field(
        default=None,
        description="Specific mechanisms, delivery methods, or patient populations to focus on"
    )
    budget_constraints: Optional[str] = Field(
        default=None,
        description="Budget considerations (e.g., 'low-cost', 'standard', 'high-end')"
    )
    timeline: Optional[str] = Field(
        default=None,
        description="Expected timeline for development (e.g., 'rapid', 'standard', 'long-term')"
    )


class HypothesisRequest(BaseModel):
    """Request schema for creating a new hypothesis"""
    goal: str = Field(
        ...,
        min_length=10,
        max_length=500,
        description="High-level goal or medical challenge to address",
        examples=["Βελτίωση ινσουλινικής ευαισθησίας στον διαβήτη τύπου 2"]
    )
    domain: MedicalDomain = Field(
        ...,
        description="Primary medical domain for the hypothesis"
    )
    constraints: Optional[HypothesisConstraints] = Field(
        default=None,
        description="Constraints and preferences for hypothesis generation"
    )
    cross_domains: Optional[List[str]] = Field(
        default=["clinical", "materials", "nanomedicine", "bioinformatics"],
        description="Cross-domain sources to search for innovative ideas"
    )
    max_runtime_minutes: int = Field(
        default=8,
        ge=1,
        le=30,
        description="Maximum runtime for hypothesis generation in minutes"
    )
    user_id: Optional[str] = Field(
        default=None,
        description="User ID for tracking and provenance"
    )

    @field_validator('goal')
    @classmethod
    def validate_goal(cls, v: str) -> str:
        if len(v.strip()) < 10:
            raise ValueError("Goal must be at least 10 characters long")
        return v.strip()


class ConceptNode(BaseModel):
    """A single concept in the concept map"""
    term: str = Field(..., description="The term or concept")
    definition: str = Field(..., description="Definition of the term")
    related_terms: List[str] = Field(default_factory=list, description="Related terms")
    pathways: List[str] = Field(default_factory=list, description="Biological pathways involved")
    targets: List[str] = Field(default_factory=list, description="Molecular targets")


class ConceptMap(BaseModel):
    """Concept map for the hypothesis"""
    concepts: List[ConceptNode] = Field(default_factory=list, description="List of concepts")
    relationships: Dict[str, List[str]] = Field(
        default_factory=dict,
        description="Relationships between concepts"
    )


class EvidencePack(BaseModel):
    """Evidence pack with supporting citations"""
    source: str = Field(..., description="Source database (PubMed, Zenodo, etc.)")
    title: str = Field(..., description="Title of the evidence")
    citation: str = Field(..., description="Full citation")
    url: Optional[str] = Field(None, description="URL to the source")
    relevance_score: float = Field(..., ge=0.0, le=1.0, description="Relevance score")
    quality_score: float = Field(..., ge=0.0, le=1.0, description="Quality score")
    key_findings: List[str] = Field(default_factory=list, description="Key findings")
    excerpts: List[str] = Field(default_factory=list, description="Relevant excerpts")


class CrossDomainTransfer(BaseModel):
    """Cross-domain idea transfer"""
    model_config = {"extra": "allow"}  # Allow backward compatibility fields
    
    source_domain: str = Field(..., description="Source domain")
    target_domain: str = Field(..., description="Target medical domain")
    concept: str = Field(..., description="Transferable concept")
    rationale: str = Field(..., description="Rationale for transfer")
    potential_impact: str = Field(..., description="Potential clinical impact")


class SimulationScorecard(BaseModel):
    """Feasibility scorecard from simulation agent"""
    model_config = {"extra": "allow"}  # Allow additional fields from AI agents
    
    therapeutic_potential: float = Field(..., ge=0.0, le=1.0)
    delivery_feasibility: float = Field(..., ge=0.0, le=1.0)
    safety_profile: float = Field(..., ge=0.0, le=1.0)
    clinical_translatability: float = Field(..., ge=0.0, le=1.0)
    overall_feasibility: Optional[str] = Field(None, description="Overall feasibility rating: GREEN/AMBER/RED")
    domain_specific_scores: Dict[str, float] = Field(default_factory=dict)
    assumptions: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)


class EthicsReport(BaseModel):
    """Ethics validation report"""
    verdict: FeasibilityLevel = Field(..., description="Overall ethics verdict")
    safety_concerns: List[str] = Field(default_factory=list)
    regulatory_considerations: List[str] = Field(default_factory=list)
    ethical_flags: List[str] = Field(default_factory=list)
    vulnerable_populations: List[str] = Field(default_factory=list)
    recommended_safeguards: List[str] = Field(default_factory=list)
    cost_effectiveness: Optional[str] = None


class HypothesisDocument(BaseModel):
    """Main hypothesis document"""
    model_config = {"extra": "allow"}  # Allow additional fields from AI agents
    
    title: str = Field(..., description="Hypothesis title")
    abstract: Optional[str] = Field(None, description="Hypothesis abstract/summary")
    mechanism_of_action: str = Field(..., description="Proposed mechanism of action")
    molecular_targets: List[str] = Field(default_factory=list)
    pathway_impact: str = Field(..., description="Expected pathway impact")
    delivery_options: List[str] = Field(default_factory=list)
    expected_outcomes: str = Field(..., description="Expected clinical outcomes")
    resistance_considerations: Optional[str] = None
    clinical_rationale: str = Field(..., description="Clinical rationale")
    novelty_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Novelty score (0-1)")


class Provenance(BaseModel):
    """Provenance tracking"""
    agent: str = Field(..., description="Agent that generated the data")
    sources: List[str] = Field(default_factory=list, description="Data sources used")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    reasoning: Optional[str] = Field(None, description="Why this agent made its decisions")


class ReasoningStep(BaseModel):
    """Single reasoning step with transparent justification - Nobel-Level feature"""
    agent: str = Field(..., description="Which agent performed this step")
    action: str = Field(..., description="What action was taken")
    input_summary: str = Field(..., description="What data was analyzed")
    reasoning: str = Field(..., description="WHY this decision was made")
    alternatives_considered: List[str] = Field(default_factory=list, description="Other options evaluated")
    decision_rationale: str = Field(..., description="Why this path was chosen over alternatives")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Decision confidence (0-1)")
    supporting_evidence: List[str] = Field(default_factory=list, description="Evidence IDs supporting this decision")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    # Narrative fields for storytelling
    question_asked: Optional[str] = Field(None, description="What question did this step answer?")
    key_insight: Optional[str] = Field(None, description="Main insight from this step")
    impact_on_hypothesis: Optional[str] = Field(None, description="How this affects the final hypothesis")


class ExecutiveSummary(BaseModel):
    """Executive summary for medical researchers - Nobel Phase 2"""
    elevator_pitch: str = Field(
        ...,
        description="2-3 sentence clear statement: We propose X to treat Y because Z"
    )
    current_treatment_gap: str = Field(
        ...,
        description="Why current treatments are failing - the clinical gap"
    )
    key_innovation: str = Field(
        ...,
        description="What's novel about this approach (in plain language)"
    )
    biological_rationale: str = Field(
        ...,
        description="Why this should work - the mechanistic justification"
    )
    priority_actions: List[str] = Field(
        default_factory=list,
        description="What a researcher should do first (test X, measure Y, try Z)"
    )
    evidence_strength: str = Field(
        ...,
        description="Why this theory has scientific merit (strong/moderate/emerging evidence)"
    )
    feasibility_verdict: str = Field(
        ...,
        description="GREEN/AMBER/RED with explanation why"
    )
    estimated_timeline: str = Field(
        ...,
        description="Realistic timeline to clinical validation (months/years)"
    )
    estimated_cost: str = Field(
        ...,
        description="Budget range (low/medium/high with reasoning)"
    )
    success_probability: str = Field(
        ...,
        description="Likelihood of success with justification (e.g., '60% - strong preclinical data')"
    )


class HypothesisSummary(BaseModel):
    """Summary of hypothesis results"""
    title: str
    feasibility: FeasibilityLevel
    ethics_verdict: FeasibilityLevel
    key_scores: Dict[str, float]


class HypothesisResponse(BaseModel):
    """Complete hypothesis response"""
    id: str = Field(..., description="Unique hypothesis ID")
    status: HypothesisStatus = Field(..., description="Current status")
    domain: MedicalDomain = Field(..., description="Medical domain")
    summary: Optional[HypothesisSummary] = None
    concept_map: Optional[ConceptMap] = None
    hypothesis_document: Optional[HypothesisDocument] = None
    evidence_packs: List[EvidencePack] = Field(default_factory=list)
    cross_domain_transfers: List[CrossDomainTransfer] = Field(default_factory=list)
    simulation_scorecard: Optional[SimulationScorecard] = None
    ethics_report: Optional[EthicsReport] = None
    provenance: List[Provenance] = Field(default_factory=list)
    # Nobel Phase 2: Executive Summary for Medical Researchers
    executive_summary: Optional[ExecutiveSummary] = Field(
        default=None,
        description="Plain-language executive summary answering: What, Why, How, What Next"
    )
    # Nobel Phase 1: Transparent Reasoning
    reasoning_steps: List[ReasoningStep] = Field(
        default_factory=list,
        description="Step-by-step reasoning process showing how decisions were made"
    )
    reasoning_narrative: Optional[str] = Field(
        default=None,
        description="Human-readable narrative explaining the decision-making process"
    )
    reasoning_flowchart: Optional[str] = Field(
        default=None,
        description="Mermaid flowchart visualizing the reasoning chain"
    )
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


class HypothesisCreateResponse(BaseModel):
    """Response for hypothesis creation (async)"""
    id: str = Field(..., description="Unique hypothesis ID")
    status: HypothesisStatus = Field(..., description="Current status")
    message: str = Field(..., description="Status message")


class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    services: Dict[str, bool] = Field(default_factory=dict, description="Service availability")


class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
