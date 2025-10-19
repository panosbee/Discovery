"""
Smart Evidence Deduplication

Removes duplicate evidence using:
- Exact title matching
- Fuzzy title similarity
- DOI/PMID cross-referencing
- URL matching
"""

from typing import List, Dict, Any
from difflib import SequenceMatcher
import re
from loguru import logger


class EvidenceDeduplicator:
    """
    Intelligent deduplication of evidence from multiple sources
    """
    
    def __init__(self, similarity_threshold: float = 0.85):
        """
        Args:
            similarity_threshold: Threshold for fuzzy title matching (0-1)
        """
        self.similarity_threshold = similarity_threshold
    
    def deduplicate(
        self,
        evidence_packs: List[Dict[str, Any]],
        keep_highest_quality: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Remove duplicate evidence from list
        
        Args:
            evidence_packs: List of evidence pack dictionaries
            keep_highest_quality: If True, keep the highest quality version of duplicates
            
        Returns:
            Deduplicated list of evidence packs
        """
        if not evidence_packs:
            return []
        
        unique_evidence = []
        seen_signatures = set()
        
        for evidence in evidence_packs:
            # Create signature for this evidence
            signature = self._create_signature(evidence)
            
            # Check if we've seen this exact signature
            if signature in seen_signatures:
                logger.debug(f"Skipping exact duplicate: {evidence.get('title', '')[:50]}")
                continue
            
            # Check for fuzzy duplicates
            is_duplicate = False
            duplicate_index = -1
            
            for idx, existing in enumerate(unique_evidence):
                if self._is_fuzzy_duplicate(evidence, existing):
                    is_duplicate = True
                    duplicate_index = idx
                    break
            
            if is_duplicate:
                if keep_highest_quality:
                    # Keep the higher quality version
                    existing = unique_evidence[duplicate_index]
                    if self._get_quality_score(evidence) > self._get_quality_score(existing):
                        logger.debug(f"Replacing with higher quality: {evidence.get('title', '')[:50]}")
                        unique_evidence[duplicate_index] = evidence
                        seen_signatures.remove(self._create_signature(existing))
                        seen_signatures.add(signature)
                    else:
                        logger.debug(f"Keeping existing higher quality: {existing.get('title', '')[:50]}")
                else:
                    logger.debug(f"Skipping fuzzy duplicate: {evidence.get('title', '')[:50]}")
            else:
                # Add new unique evidence
                unique_evidence.append(evidence)
                seen_signatures.add(signature)
        
        removed_count = len(evidence_packs) - len(unique_evidence)
        if removed_count > 0:
            logger.info(f"Removed {removed_count} duplicate evidence packs ({len(unique_evidence)} unique)")
        
        return unique_evidence
    
    def _create_signature(self, evidence: Dict[str, Any]) -> str:
        """
        Create a unique signature for evidence based on identifiers
        """
        # Try DOI first (most reliable)
        doi = self._extract_doi(evidence)
        if doi:
            return f"doi:{doi}"
        
        # Try PMID
        pmid = self._extract_pmid(evidence)
        if pmid:
            return f"pmid:{pmid}"
        
        # Try NCT ID (clinical trials)
        nct_id = self._extract_nct_id(evidence)
        if nct_id:
            return f"nct:{nct_id}"
        
        # Try arXiv ID
        arxiv_id = self._extract_arxiv_id(evidence)
        if arxiv_id:
            return f"arxiv:{arxiv_id}"
        
        # Try URL
        url = evidence.get("url", "")
        if url:
            # Normalize URL (remove protocol, trailing slashes, query params)
            normalized_url = re.sub(r'^https?://', '', url)
            normalized_url = normalized_url.rstrip('/').split('?')[0]
            return f"url:{normalized_url}"
        
        # Fallback to normalized title
        title = evidence.get("title", "").lower().strip()
        title = re.sub(r'[^\w\s]', '', title)  # Remove punctuation
        title = re.sub(r'\s+', ' ', title)     # Normalize whitespace
        return f"title:{title}"
    
    def _is_fuzzy_duplicate(
        self,
        evidence1: Dict[str, Any],
        evidence2: Dict[str, Any]
    ) -> bool:
        """
        Check if two evidence pieces are fuzzy duplicates
        """
        # Check for ID overlap
        doi1, doi2 = self._extract_doi(evidence1), self._extract_doi(evidence2)
        if doi1 and doi2 and doi1 == doi2:
            return True
        
        pmid1, pmid2 = self._extract_pmid(evidence1), self._extract_pmid(evidence2)
        if pmid1 and pmid2 and pmid1 == pmid2:
            return True
        
        # Check title similarity (handle None values)
        title1 = evidence1.get("title") or ""
        title2 = evidence2.get("title") or ""
        title1 = title1.lower().strip()
        title2 = title2.lower().strip()
        
        if not title1 or not title2:
            return False
        
        similarity = self._calculate_string_similarity(title1, title2)
        
        if similarity >= self.similarity_threshold:
            logger.debug(f"Fuzzy match (similarity={similarity:.2f}): '{title1[:50]}' ≈ '{title2[:50]}'")
            return True
        
        return False
    
    def _calculate_string_similarity(self, str1: str, str2: str) -> float:
        """
        Calculate similarity between two strings using SequenceMatcher
        """
        return SequenceMatcher(None, str1, str2).ratio()
    
    def _extract_doi(self, evidence: Dict[str, Any]) -> str:
        """
        Extract DOI from evidence
        """
        # Check URL
        url = evidence.get("url", "")
        doi_match = re.search(r'10\.\d{4,}/[^\s]+', url)
        if doi_match:
            return doi_match.group(0).rstrip('/')
        
        # Check citation
        citation = evidence.get("citation", "")
        doi_match = re.search(r'10\.\d{4,}/[^\s,;]+', citation)
        if doi_match:
            return doi_match.group(0).rstrip('.,;')
        
        return ""
    
    def _extract_pmid(self, evidence: Dict[str, Any]) -> str:
        """
        Extract PubMed ID (PMID) from evidence
        """
        citation = evidence.get("citation", "")
        url = evidence.get("url", "")
        
        # Check URL for PMID
        pmid_match = re.search(r'pubmed/(\d+)', url)
        if pmid_match:
            return pmid_match.group(1)
        
        # Check citation
        pmid_match = re.search(r'PMID:?\s*(\d+)', citation, re.IGNORECASE)
        if pmid_match:
            return pmid_match.group(1)
        
        return ""
    
    def _extract_nct_id(self, evidence: Dict[str, Any]) -> str:
        """
        Extract NCT ID (ClinicalTrials.gov) from evidence
        """
        citation = evidence.get("citation", "")
        url = evidence.get("url", "")
        
        # NCT ID pattern
        nct_match = re.search(r'NCT\d{8}', citation + " " + url, re.IGNORECASE)
        if nct_match:
            return nct_match.group(0).upper()
        
        return ""
    
    def _extract_arxiv_id(self, evidence: Dict[str, Any]) -> str:
        """
        Extract arXiv ID from evidence
        """
        citation = evidence.get("citation", "")
        url = evidence.get("url", "")
        
        # arXiv ID pattern (e.g., 2103.12345)
        arxiv_match = re.search(r'arxiv:?\s*(\d{4}\.\d{4,5})', citation + " " + url, re.IGNORECASE)
        if arxiv_match:
            return arxiv_match.group(1)
        
        return ""
    
    def _get_quality_score(self, evidence: Dict[str, Any]) -> float:
        """
        Get quality score from evidence (if available)
        """
        # Try confidence_score first (from enhanced scoring)
        if "confidence_score" in evidence:
            return evidence["confidence_score"]
        
        # Fallback to quality_score
        if "quality_score" in evidence:
            return evidence["quality_score"]
        
        # Default
        return 0.5
    
    def merge_duplicate_evidence(
        self,
        evidence_packs: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Merge duplicate evidence by combining information
        (Alternative to simple deduplication)
        """
        merged = []
        groups: Dict[str, List[Dict[str, Any]]] = {}
        
        # Group by signature
        for evidence in evidence_packs:
            signature = self._create_signature(evidence)
            if signature not in groups:
                groups[signature] = []
            groups[signature].append(evidence)
        
        # Merge each group
        for signature, group in groups.items():
            if len(group) == 1:
                merged.append(group[0])
            else:
                # Merge multiple evidence pieces
                merged_evidence = self._merge_evidence_group(group)
                merged.append(merged_evidence)
                logger.debug(f"Merged {len(group)} evidence pieces: {merged_evidence.get('title', '')[:50]}")
        
        return merged
    
    def _merge_evidence_group(
        self,
        group: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Merge multiple evidence pieces into one comprehensive piece
        """
        # Start with the highest quality piece
        sorted_group = sorted(
            group,
            key=lambda x: self._get_quality_score(x),
            reverse=True
        )
        merged = sorted_group[0].copy()
        
        # Merge key_findings from all sources
        all_findings = []
        for evidence in group:
            findings = evidence.get("key_findings", [])
            all_findings.extend(findings)
        merged["key_findings"] = list(set(all_findings))  # Remove duplicates
        
        # Merge excerpts
        all_excerpts = []
        for evidence in group:
            excerpts = evidence.get("excerpts", [])
            all_excerpts.extend(excerpts)
        merged["excerpts"] = list(set(all_excerpts))[:3]  # Keep top 3 unique
        
        # Combine sources
        sources = [e.get("source", "") for e in group]
        unique_sources = list(set(sources))
        if len(unique_sources) > 1:
            merged["source"] = f"{merged['source']} (also in: {', '.join(unique_sources[1:])})"
        
        # Use highest scores
        if "confidence_score" in merged:
            merged["confidence_score"] = max(
                e.get("confidence_score", 0) for e in group
            )
        
        return merged
