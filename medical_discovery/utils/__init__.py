"""
Utility modules for Medical Discovery System
"""

from medical_discovery.utils.evidence_scorer import EvidenceScorer
from medical_discovery.utils.query_expander import QueryExpander
from medical_discovery.utils.evidence_deduplicator import EvidenceDeduplicator

__all__ = [
    "EvidenceScorer",
    "QueryExpander",
    "EvidenceDeduplicator",
]
