"""
Epistemic Metadata Extraction Utility

Best-effort extraction of study type, sample size, and epistemic weight
from PubMed abstracts, ClinicalTrials records, and other evidence sources.

Part of Nobel Architecture 3.0 LITE.
"""

import re
from typing import Dict, Optional


# Study type weights based on evidence hierarchy
STUDY_TYPE_WEIGHTS = {
    "meta_analysis": 1.0,
    "systematic_review": 0.95,
    "rct": 0.9,
    "cohort": 0.75,
    "case_control": 0.6,
    "in_vivo": 0.55,  # Animal models - important for therapeutic validation
    "cross_sectional": 0.5,
    "review": 0.5,
    "case_report": 0.4,
    "preprint": 0.35,
    "in_vitro": 0.3,
    "in_silico": 0.25,
    "unknown": 0.25  # Lowered from 0.4 - low-trust mapping
}


def extract_epistemic_tags(evidence_dict: Dict) -> Dict:
    """
    Extract epistemic metadata from evidence.
    
    Args:
        evidence_dict: Raw evidence from connector with fields:
            - abstract (str): Paper abstract
            - title (str): Paper title
            - publication_type (str, optional): MeSH publication type
            - study_type (str, optional): Explicit study type from API
            - metadata (dict, optional): Additional metadata
    
    Returns:
        {
            "study_type": str,
            "sample_size": int or None,
            "weight": float (0.0-1.0),
            "confidence": float (0.0-1.0)  # extraction confidence
        }
    """
    abstract = evidence_dict.get("abstract", "")
    title = evidence_dict.get("title", "")
    publication_type = evidence_dict.get("publication_type", "")
    venue = evidence_dict.get("venue", "") or evidence_dict.get("journal", "")
    metadata = evidence_dict.get("metadata", {})
    
    # Try explicit study_type first (from API)
    study_type = evidence_dict.get("study_type")
    confidence = 1.0 if study_type else 0.0
    
    # Fallback: detect from text + venue
    if not study_type:
        study_type, confidence = detect_study_type(abstract, title, publication_type, venue)
    
    # Extract sample size
    sample_size = extract_sample_size(abstract, metadata)
    
    # Get epistemic weight (default to 0.25 for unknown)
    weight = STUDY_TYPE_WEIGHTS.get(study_type, 0.25)
    
    # Adjust weight by sample size (if available)
    if sample_size:
        if sample_size >= 1000:
            weight = min(weight * 1.1, 1.0)
        elif sample_size < 50:
            weight *= 0.9
    
    return {
        "study_type": study_type,
        "sample_size": sample_size,
        "weight": round(weight, 2),
        "confidence": round(confidence, 2)
    }


def detect_study_type(abstract: str, title: str, publication_type: str = "", venue: str = "") -> tuple[str, float]:
    """
    Detect study type from abstract/title text + venue.
    
    Args:
        abstract: Abstract text
        title: Title text  
        publication_type: Explicit publication type if known
        venue: Journal/venue name for mapping
        
    Returns:
        (study_type, confidence)
    """
    text = f"{title.lower()} {abstract.lower()} {publication_type.lower()} {venue.lower()}"
    
    # Venue-based mapping (high confidence)
    venue_lower = venue.lower()
    if any(term in venue_lower for term in ["nature reviews", "annual review", "trends in"]):
        return "review", 0.90
    
    if "arxiv" in venue_lower or "biorxiv" in venue_lower or "medrxiv" in venue_lower:
        return "preprint", 0.95
    
    # High-confidence patterns (explicit mentions)
    if any(term in text for term in ["meta-analysis", "meta analysis", "metaanalysis"]):
        return "meta_analysis", 0.95
    
    if any(term in text for term in ["systematic review"]):
        return "systematic_review", 0.95
    
    if any(term in text for term in ["randomized controlled trial", "rct", "randomised", 
                                      "double-blind", "placebo-controlled", "randomized trial"]):
        return "rct", 0.90
    
    if any(term in text for term in ["cohort study", "prospective study", "longitudinal study", 
                                      "prospective cohort"]):
        return "cohort", 0.85
    
    if any(term in text for term in ["case-control study", "case control", "case-control"]):
        return "case_control", 0.85
    
    # Medium-confidence patterns
    if any(term in text for term in ["in vitro", "cell culture", "cultured cells", "cell-based", 
                                      "cell line", "in vitro study"]):
        return "in_vitro", 0.75
    
    if any(term in text for term in ["in silico", "computational model", "simulation", 
                                      "molecular dynamics", "bioinformatics", "machine learning",
                                      "deep learning", "structural modeling"]):
        return "in_silico", 0.75
    
    if any(term in text for term in ["cross-sectional", "cross sectional", "observational study",
                                      "retrospective analysis"]):
        return "cross_sectional", 0.80
    
    if any(term in text for term in ["case report", "case series"]):
        return "case_report", 0.80
    
    # Animal models (important for therapeutic research)
    if any(term in text for term in ["mouse model", "murine", "xenograft", "orthotopic",
                                      "animal model", "preclinical", "in vivo"]):
        return "in_vivo", 0.70
    
    # Low-confidence patterns
    if "review" in text and "systematic" not in text:
        return "review", 0.60
    
    if any(term in text for term in ["preprint", "biorxiv", "medrxiv"]):
        return "preprint", 0.90
    
    # Default - low trust
    return "unknown", 0.25  # Lowered confidence for unknown mapping


def extract_sample_size(abstract: str, metadata: Dict) -> Optional[int]:
    """
    Extract sample size (n) from abstract or metadata.
    
    Patterns:
    - "n = 120 patients"
    - "120 participants"
    - "sample of 120"
    - "enrolled 120 subjects"
    """
    # Try metadata first
    if "sample_size" in metadata:
        return metadata["sample_size"]
    
    if not abstract:
        return None
    
    text = abstract.lower()
    
    # Pattern 1: "n = 120" or "n=120"
    match = re.search(r'n\s*=\s*(\d+)', text)
    if match:
        return int(match.group(1))
    
    # Pattern 2: "120 patients/participants/subjects"
    match = re.search(r'(\d+)\s+(patients|participants|subjects|individuals|cases)', text)
    if match:
        return int(match.group(1))
    
    # Pattern 3: "enrolled 120" or "included 120"
    match = re.search(r'(enrolled|included|recruited)\s+(\d+)', text)
    if match:
        return int(match.group(2))
    
    # Pattern 4: "sample of 120" or "cohort of 120"
    match = re.search(r'(sample|cohort)\s+of\s+(\d+)', text)
    if match:
        return int(match.group(2))
    
    return None


def calculate_evidence_strength_v2(evidence_packs: list) -> Dict:
    """
    Calculate evidence strength weighted by epistemic quality (v2).
    
    Args:
        evidence_packs: List of evidence packs from EvidenceMinerAgent
        
    Returns:
        {
            "strength_v2": float (0.0-1.0),
            "total_evidence": int,
            "study_type_breakdown": {study_type: count},
            "weighted_total": float
        }
    """
    all_evidence = []
    for pack in evidence_packs:
        # Support two pack shapes:
        # 1) Wrapped packs: {"source":..., "evidence": [item, ...]}
        # 2) Flat evidence items: each pack is an evidence item dict
        if isinstance(pack, dict) and isinstance(pack.get("evidence", None), list):
            all_evidence.extend(pack.get("evidence", []))
        elif isinstance(pack, dict) and ("epistemic_metadata" in pack or "title" in pack or "citation" in pack):
            # Treat the pack itself as a single evidence item
            all_evidence.append(pack)
        else:
            # Unknown shape: skip safely
            continue
    
    if not all_evidence:
        return {
            "strength_v2": 0.0,
            "total_evidence": 0,
            "study_type_breakdown": {},
            "weighted_total": 0.0
        }
    
    # Calculate weighted sum
    weighted_sum = 0.0
    study_type_counts = {}
    
    for ev in all_evidence:
        epistemic = ev.get("epistemic_metadata", {})
        weight = epistemic.get("weight", 0.4)  # fallback if no epistemic tags
        study_type = epistemic.get("study_type", "unknown")
        
        weighted_sum += weight
        study_type_counts[study_type] = study_type_counts.get(study_type, 0) + 1
    
    # Maximum possible weight (if all were meta-analyses)
    max_weight = len(all_evidence) * 1.0
    
    # Normalized strength
    strength_v2 = min(weighted_sum / max_weight, 1.0) if max_weight > 0 else 0.0
    
    return {
        "strength_v2": round(strength_v2, 2),
        "total_evidence": len(all_evidence),
        "study_type_breakdown": study_type_counts,
        "weighted_total": round(weighted_sum, 2)
    }


def format_epistemic_confidence(strength_v2_data: Dict) -> str:
    """
    Format epistemic confidence for narrative display.
    
    Returns:
        Markdown section for executive summary
    """
    strength = strength_v2_data["strength_v2"]
    total = strength_v2_data["total_evidence"]
    breakdown = strength_v2_data["study_type_breakdown"]
    
    # Sort by weight descending
    sorted_types = sorted(breakdown.items(), 
                         key=lambda x: STUDY_TYPE_WEIGHTS.get(x[0], 0.4), 
                         reverse=True)
    
    lines = [
        "## 🧬 Epistemic Confidence",
        "",
        f"**Evidence Strength**: {strength:.2f} (epistemic-weighted, n={total})",
        ""
    ]
    
    if sorted_types:
        lines.append("**Study Type Breakdown**:")
        for study_type, count in sorted_types:
            weight = STUDY_TYPE_WEIGHTS.get(study_type, 0.4)
            emoji = "🟢" if weight >= 0.8 else "🟡" if weight >= 0.6 else "🟠"
            display_name = study_type.replace("_", " ").title()
            lines.append(f"- {emoji} {display_name}: {count} (weight: {weight})")
    
    return "\n".join(lines)
