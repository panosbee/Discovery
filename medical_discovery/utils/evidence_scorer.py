"""
Enhanced Evidence Quality & Relevance Scoring

Provides sophisticated scoring algorithms for evidence evaluation.
Multi-dimensional scoring based on:
- Citation impact
- Recency (temporal relevance)
- Source credibility
- Content relevance
- Methodological rigor
"""

from typing import Dict, Any, List, Optional
from datetime import datetime
import re
from loguru import logger


class EvidenceScorer:
    """
    Advanced evidence scoring system for quality and relevance assessment
    """
    
    def __init__(self):
        # Source credibility weights (0-1 scale)
        self.source_credibility = {
            "PubMed": 0.95,          # Peer-reviewed, curated
            "Crossref": 0.90,        # DOI-registered publications
            "ClinicalTrials.gov": 0.95,  # Official clinical data
            "UniProt": 0.95,         # Expert-curated protein data
            "KEGG": 0.90,            # Curated pathway database
            "ChEMBL": 0.90,          # Bioactivity data, peer-reviewed
            "PubChem": 0.85,         # Large scale, automated
            "arXiv": 0.70,           # Preprints, not peer-reviewed
            "Zenodo": 0.75,          # Open datasets, variable quality
            "Kaggle": 0.70,          # Community datasets, variable quality
        }
        
        # Journal impact tier (can be expanded with actual impact factors)
        self.high_impact_journals = [
            "nature", "science", "cell", "lancet", "nejm", "jama",
            "pnas", "nature medicine", "nature biotechnology"
        ]
        
    def calculate_comprehensive_score(
        self,
        evidence: Dict[str, Any],
        query_terms: List[str],
        domain: str
    ) -> Dict[str, float]:
        """
        Calculate comprehensive evidence score across multiple dimensions
        
        Returns:
            Dict with scores:
            - relevance_score: How relevant to the query (0-1)
            - quality_score: Quality of the evidence (0-1)
            - recency_score: Temporal relevance (0-1)
            - impact_score: Citation/usage impact (0-1)
            - confidence_score: Overall confidence (weighted average)
        """
        scores = {}
        
        # 1. Relevance Score (enhanced with term matching)
        scores["relevance_score"] = self._calculate_relevance(
            evidence, query_terms
        )
        
        # 2. Quality Score (based on source + methodology)
        scores["quality_score"] = self._calculate_quality(evidence)
        
        # 3. Recency Score (temporal decay)
        scores["recency_score"] = self._calculate_recency(evidence)
        
        # 4. Impact Score (citations, downloads, usage)
        scores["impact_score"] = self._calculate_impact(evidence)
        
        # 5. Confidence Score (weighted combination)
        scores["confidence_score"] = self._calculate_confidence(scores)
        
        return scores
    
    def _calculate_relevance(
        self,
        evidence: Dict[str, Any],
        query_terms: List[str]
    ) -> float:
        """
        Calculate relevance score based on term matching and semantic similarity
        """
        if not query_terms:
            return 0.5  # Default if no query terms
        
        title = (evidence.get("title") or "").lower()
        excerpts = " ".join(evidence.get("excerpts", [])).lower()
        key_findings = " ".join(evidence.get("key_findings", [])).lower()
        
        combined_text = f"{title} {excerpts} {key_findings}"
        
        # Count term matches
        term_matches = 0
        for term in query_terms:
            term_lower = term.lower()
            # Exact matches
            if term_lower in combined_text:
                term_matches += 1
            # Partial matches (for compound terms)
            elif any(word in combined_text for word in term_lower.split()):
                term_matches += 0.5
        
        # Normalize by number of terms
        relevance = min(term_matches / len(query_terms), 1.0)
        
        # Bonus for title matches (title is more important)
        title_matches = sum(1 for term in query_terms if term.lower() in title)
        if title_matches > 0:
            relevance = min(relevance + (title_matches * 0.1), 1.0)
        
        return round(relevance, 3)
    
    def _calculate_quality(self, evidence: Dict[str, Any]) -> float:
        """
        Calculate quality score based on source credibility and content indicators
        """
        source = evidence.get("source", "")
        base_quality = self.source_credibility.get(source, 0.5)
        
        # Adjust based on content indicators
        citation = evidence.get("citation", "").lower()
        
        # Bonus for high-impact journals
        if any(journal in citation for journal in self.high_impact_journals):
            base_quality = min(base_quality + 0.05, 1.0)
        
        # Bonus for peer-reviewed indicators
        if any(indicator in citation for indicator in ["peer-reviewed", "published", "journal"]):
            base_quality = min(base_quality + 0.02, 1.0)
        
        # Penalty for preprints/unreviewed
        if any(indicator in citation for indicator in ["preprint", "arxiv", "biorxiv"]):
            base_quality = max(base_quality - 0.05, 0.3)
        
        # Bonus for having key findings
        if evidence.get("key_findings") and len(evidence["key_findings"]) > 0:
            base_quality = min(base_quality + 0.03, 1.0)
        
        return round(base_quality, 3)
    
    def _calculate_recency(self, evidence: Dict[str, Any]) -> float:
        """
        Calculate recency score with exponential decay
        Newer evidence gets higher scores
        """
        citation = evidence.get("citation", "")
        
        # Extract year from citation
        year_match = re.search(r'\b(19|20)\d{2}\b', citation)
        if not year_match:
            return 0.5  # Default if no year found
        
        pub_year = int(year_match.group(0))
        current_year = datetime.now().year
        
        years_old = current_year - pub_year
        
        # Exponential decay: e^(-years/halflife)
        # halflife = 5 years (research from 5 years ago gets 0.5 score)
        import math
        halflife = 5.0
        recency = math.exp(-years_old / halflife)
        
        return round(recency, 3)
    
    def _calculate_impact(self, evidence: Dict[str, Any]) -> float:
        """
        Calculate impact score based on citations, downloads, votes
        """
        citation = evidence.get("citation", "").lower()
        source = evidence.get("source", "")
        
        impact = 0.5  # Base impact
        
        # Extract citation count if available
        citation_match = re.search(r'(\d+)\s+citation', citation)
        if citation_match:
            citations = int(citation_match.group(1))
            # Logarithmic scaling for citations
            import math
            impact = min(0.3 + (math.log10(citations + 1) / 4), 1.0)
        
        # Check for download/usage indicators
        if "downloads" in citation:
            download_match = re.search(r'(\d+)\s+download', citation)
            if download_match:
                downloads = int(download_match.group(1))
                impact = max(impact, min(0.4 + (math.log10(downloads + 1) / 5), 1.0))
        
        # Bonus for clinical trials (high impact by nature)
        if source == "ClinicalTrials.gov":
            impact = max(impact, 0.8)
        
        # Bonus for votes (Kaggle, Zenodo)
        if "votes" in citation:
            vote_match = re.search(r'(\d+)\s+vote', citation)
            if vote_match:
                votes = int(vote_match.group(1))
                impact = max(impact, min(0.5 + (votes / 100), 0.9))
        
        return round(impact, 3)
    
    def _calculate_confidence(self, scores: Dict[str, float]) -> float:
        """
        Calculate overall confidence as weighted combination of all scores
        """
        weights = {
            "relevance_score": 0.35,    # Most important
            "quality_score": 0.30,      # Very important
            "impact_score": 0.20,       # Important
            "recency_score": 0.15,      # Moderately important
        }
        
        confidence = sum(
            scores.get(key, 0.5) * weight
            for key, weight in weights.items()
        )
        
        return round(confidence, 3)
    
    def rank_evidence_packs(
        self,
        evidence_packs: List[Dict[str, Any]],
        top_k: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Rank evidence packs by confidence score and return top K
        """
        # Sort by confidence score (descending)
        ranked = sorted(
            evidence_packs,
            key=lambda x: x.get("confidence_score", 0),
            reverse=True
        )
        
        if top_k:
            return ranked[:top_k]
        return ranked
    
    def get_evidence_tier(self, confidence_score: float) -> str:
        """
        Classify evidence into tiers based on confidence score
        """
        if confidence_score >= 0.85:
            return "TIER_1_EXCEPTIONAL"
        elif confidence_score >= 0.75:
            return "TIER_2_HIGH"
        elif confidence_score >= 0.60:
            return "TIER_3_MODERATE"
        elif confidence_score >= 0.45:
            return "TIER_4_LOW"
        else:
            return "TIER_5_MARGINAL"
