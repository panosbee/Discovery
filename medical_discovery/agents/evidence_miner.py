"""
Evidence Miner Agent
Gathers supporting evidence from multiple scientific databases with advanced intelligence
"""
from loguru import logger
from typing import Dict, Any, List

from medical_discovery.data.connectors.pubmed_connector import PubMedConnector
from medical_discovery.data.connectors.zenodo_connector import ZenodoConnector
from medical_discovery.data.connectors.clinicaltrials_connector import ClinicalTrialsConnector
from medical_discovery.data.connectors.pubchem_connector import PubChemConnector
from medical_discovery.data.connectors.chembl_connector import ChEMBLConnector
from medical_discovery.data.connectors.crossref_connector import CrossrefConnector
from medical_discovery.data.connectors.arxiv_connector import ArxivConnector
from medical_discovery.data.connectors.uniprot_connector import UniProtConnector
from medical_discovery.data.connectors.kegg_connector import KEGGConnector
from medical_discovery.data.connectors.kaggle_connector import KaggleConnector
from medical_discovery.services.deepseek_client import deepseek_client
from medical_discovery.api.schemas.hypothesis import EvidencePack
from medical_discovery.utils import EvidenceScorer, QueryExpander, EvidenceDeduplicator


class EvidenceMinerAgent:
    """
    Mines evidence from scientific literature and databases with Nobel-level intelligence
    
    Features:
    - Multi-source data gathering (10 connectors)
    - Intelligent query expansion with medical ontology
    - Advanced evidence scoring (relevance, quality, recency, impact)
    - Smart deduplication with fuzzy matching
    - Cross-source evidence linking
    
    Data Sources:
    - Publications: PubMed, Crossref, arXiv
    - Clinical Trials: ClinicalTrials.gov
    - Chemistry: PubChem, ChEMBL
    - Proteins/Genes: UniProt, KEGG
    - Datasets: Zenodo, Kaggle
    """
    
    def __init__(self):
        """Initialize Evidence Miner Agent with all data connectors and intelligence modules"""
        # Data connectors
        self.pubmed = PubMedConnector()
        self.zenodo = ZenodoConnector()
        self.clinical_trials = ClinicalTrialsConnector()
        self.pubchem = PubChemConnector()
        self.chembl = ChEMBLConnector()
        self.crossref = CrossrefConnector()
        self.arxiv = ArxivConnector()
        self.uniprot = UniProtConnector()
        self.kegg = KEGGConnector()
        self.kaggle = KaggleConnector()
        
        # Intelligence modules
        self.scorer = EvidenceScorer()
        self.query_expander = QueryExpander()
        self.deduplicator = EvidenceDeduplicator(similarity_threshold=0.85)
        
        logger.info("Evidence Miner Agent initialized with 10 data connectors + Intelligence modules")
    
    async def gather_evidence(
        self,
        concept_map: Dict[str, Any],
        domain: str,
        goal: str
    ) -> List[Dict[str, Any]]:
        """
        Gather evidence from multiple sources
        
        Args:
            concept_map: Concept map from Concept Learner
            domain: Medical domain
            goal: Research goal
            
        Returns:
            List of evidence packs
        """
        logger.info(f"Gathering evidence for domain: {domain}")
        
        evidence_packs = []
        
        # Extract search terms from concept map
        base_search_terms = self._extract_search_terms(concept_map, goal)
        logger.info(f"Extracted {len(base_search_terms)} base search terms")
        
        # === INTELLIGENCE LAYER: Query Expansion ===
        # Expand queries with medical synonyms and ontology terms
        expanded_terms = []
        for term in base_search_terms[:10]:  # Expand top 10 terms
            expanded = self.query_expander.expand_query(
                query=term,
                domain=domain,
                max_terms=3,  # Add up to 3 related terms per base term
                include_synonyms=True,
                include_domain_keywords=False  # Avoid too much expansion
            )
            expanded_terms.extend(expanded)
        
        # Remove duplicates while preserving order
        seen = set()
        search_terms = []
        for term in expanded_terms:
            if term.lower() not in seen:
                seen.add(term.lower())
                search_terms.append(term)
        
        logger.info(f"After intelligent expansion: {len(search_terms)} search terms")
        logger.debug(f"Top expanded terms: {search_terms[:5]}")
        
        # Main search query
        main_query = " ".join(search_terms[:3])
        
        # 1. Search PubMed for peer-reviewed publications
        try:
            pubmed_results = await self.pubmed.search(
                query=" OR ".join(search_terms[:5]),
                max_results=15
            )
            
            for article in pubmed_results:
                evidence_packs.append({
                    "source": "PubMed",
                    "title": article.get("title", ""),
                    "citation": article.get("citation", ""),
                    "url": article.get("url", ""),
                    "relevance_score": 0.9,
                    "quality_score": 0.9,
                    "key_findings": article.get("key_findings", []),
                    "excerpts": article.get("excerpts", []),
                    "epistemic_metadata": article.get("epistemic_metadata", {})
                })
            
            logger.success(f"Found {len(pubmed_results)} PubMed articles")
            
        except Exception as e:
            logger.error(f"PubMed search failed: {str(e)}")
        
        # 2. Search Crossref for additional publications and citations
        try:
            crossref_results = await self.crossref.search(
                query=main_query,
                max_results=10
            )
            
            for pub in crossref_results:
                evidence_packs.append({
                    "source": "Crossref",
                    "title": pub.get("title", ""),
                    "citation": f"{', '.join(pub.get('authors', [])[:3])} et al. ({pub.get('publication_year')}) {pub.get('container_title')}",
                    "url": pub.get("url", ""),
                    "relevance_score": 0.8,
                    "quality_score": 0.85,
                    "key_findings": [],
                    "excerpts": [pub.get("abstract", "")[:500]] if pub.get("abstract") else [],
                    "epistemic_metadata": {}  # Crossref doesn't provide structured epistemic data
                })
            
            logger.success(f"Found {len(crossref_results)} Crossref publications")
            
        except Exception as e:
            logger.error(f"Crossref search failed: {str(e)}")
        
        # 3. Search arXiv for preprints (especially for emerging research)
        try:
            arxiv_results = await self.arxiv.search(
                query=main_query,
                category="q-bio",  # Quantitative biology
                max_results=10
            )
            
            for preprint in arxiv_results:
                evidence_packs.append({
                    "source": "arXiv",
                    "title": preprint.get("title", ""),
                    "citation": f"{', '.join(preprint.get('authors', [])[:3])} ({preprint.get('published')}) arXiv:{preprint.get('arxiv_id')}",
                    "url": preprint.get("url", ""),
                    "relevance_score": 0.7,
                    "quality_score": 0.7,
                    "key_findings": [],
                    "excerpts": [preprint.get("summary", "")[:500]],
                    "epistemic_metadata": {}  # arXiv preprints lack structured epistemic metadata
                })
            
            logger.success(f"Found {len(arxiv_results)} arXiv preprints")
            
        except Exception as e:
            logger.error(f"arXiv search failed: {str(e)}")
        
        # 4. Search ClinicalTrials.gov for clinical evidence
        try:
            clinical_results = await self.clinical_trials.search(
                query=main_query,
                condition=domain if domain not in ["general", "multidomain"] else None,
                max_results=10
            )
            
            for trial in clinical_results:
                evidence_packs.append({
                    "source": "ClinicalTrials.gov",
                    "title": trial.get("title", ""),
                    "citation": f"{trial.get('nct_id')} - {trial.get('status')} - Phase: {', '.join(trial.get('phases', []))}",
                    "url": trial.get("url", ""),
                    "relevance_score": 0.85,
                    "quality_score": 0.9,
                    "key_findings": [o.get("measure", "") for o in trial.get("primary_outcomes", [])[:3]],
                    "excerpts": [trial.get("brief_summary", "")[:500]],
                    "epistemic_metadata": trial.get("epistemic_metadata", {})
                })
            
            logger.success(f"Found {len(clinical_results)} clinical trials")
            
        except Exception as e:
            logger.error(f"ClinicalTrials.gov search failed: {str(e)}")
        
        # 5. Search UniProt for protein/gene information (if relevant)
        if any(term in main_query.lower() for term in ["protein", "gene", "enzyme", "receptor"]):
            try:
                uniprot_results = await self.uniprot.search(
                    query=main_query,
                    reviewed=True,  # Swiss-Prot only (higher quality)
                    max_results=5
                )
                
                for protein in uniprot_results:
                    evidence_packs.append({
                        "source": "UniProt",
                        "title": f"{protein.get('protein_name')} ({protein.get('accession')})",
                        "citation": f"UniProt: {protein.get('accession')} - {protein.get('organism')}",
                        "url": protein.get("url", ""),
                        "relevance_score": 0.8,
                        "quality_score": 0.95,
                        "key_findings": [protein.get("function", "")[:200]] if protein.get("function") else [],
                        "excerpts": [],
                        "epistemic_metadata": {}  # UniProt provides protein data, not clinical studies
                    })
                
                logger.success(f"Found {len(uniprot_results)} UniProt entries")
                
            except Exception as e:
                logger.error(f"UniProt search failed: {str(e)}")
        
        # 6. Search KEGG for pathways
        try:
            # Extract broader pathway-relevant terms for KEGG (works better than specific protein names)
            pathway_terms = []
            for term in search_terms[:10]:  # Use first 10 search terms
                # Filter for pathway-relevant words
                term_lower = term.lower()
                if any(kw in term_lower for kw in ["pathway", "signaling", "metabolism", "synthesis", "degradation"]):
                    pathway_terms.append(term)
                elif len(term.split()) <= 2:  # Single or two-word terms work better
                    pathway_terms.append(term)
            
            # If no suitable terms, use domain-specific keywords
            if not pathway_terms:
                domain_pathways = {
                    "diabetes": ["insulin", "glucose"],
                    "cardiology": ["cardiac", "vascular"],
                    "oncology": ["cancer", "tumor"],
                    "neurology": ["neural", "brain"],
                    "immunology": ["immune", "cytokine"]
                }
                pathway_terms = domain_pathways.get(domain, [domain])
            
            # Search with each term and combine results
            kegg_pathways = []
            for term in pathway_terms[:3]:  # Limit to 3 terms to avoid too many requests
                pathways = await self.kegg.search_pathways(
                    query=term,
                    organism="hsa"  # Human
                )
                kegg_pathways.extend(pathways)
                if len(kegg_pathways) >= 5:
                    break
            
            # Remove duplicates by pathway_id
            seen_ids = set()
            unique_pathways = []
            for pw in kegg_pathways:
                if pw.get("pathway_id") not in seen_ids:
                    seen_ids.add(pw.get("pathway_id"))
                    unique_pathways.append(pw)
            
            for pathway in unique_pathways[:5]:  # Limit to 5 pathways
                evidence_packs.append({
                    "source": "KEGG",
                    "title": pathway.get("name", ""),
                    "citation": f"KEGG Pathway: {pathway.get('pathway_id')}",
                    "url": pathway.get("url", ""),
                    "relevance_score": 0.75,
                    "quality_score": 0.9,
                    "key_findings": [pathway.get("description", "")[:200]] if pathway.get("description") else [],
                    "excerpts": [],
                    "epistemic_metadata": {}  # KEGG provides pathway data, not clinical studies
                })
            
            logger.success(f"Found {len(unique_pathways[:5])} KEGG pathways")
            
        except Exception as e:
            logger.error(f"KEGG search failed: {str(e)}")
        
        # 7. Search PubChem for chemical compounds (if relevant)
        if any(term in main_query.lower() for term in ["compound", "drug", "molecule", "chemical"]):
            try:
                pubchem_results = await self.pubchem.search_compounds(
                    query=main_query,
                    max_results=5
                )
                
                for compound in pubchem_results:
                    evidence_packs.append({
                        "source": "PubChem",
                        "title": f"{compound.get('iupac_name', 'Compound')} (CID: {compound.get('cid')})",
                        "citation": f"PubChem CID: {compound.get('cid')} - {compound.get('molecular_formula')}",
                        "url": compound.get("url", ""),
                        "relevance_score": 0.7,
                        "quality_score": 0.85,
                        "key_findings": [f"MW: {compound.get('molecular_weight')}, Formula: {compound.get('molecular_formula')}"],
                        "excerpts": []
                    })
                
                logger.success(f"Found {len(pubchem_results)} PubChem compounds")
                
            except Exception as e:
                logger.error(f"PubChem search failed: {str(e)}")
        
        # 8. Search ChEMBL for bioactivity data (if relevant)
        if any(term in main_query.lower() for term in ["drug", "bioactivity", "target", "inhibitor"]):
            try:
                chembl_results = await self.chembl.search_molecules(
                    query=main_query,
                    max_results=5
                )
                
                for molecule in chembl_results:
                    evidence_packs.append({
                        "source": "ChEMBL",
                        "title": f"{molecule.get('pref_name', 'Molecule')} ({molecule.get('chembl_id')})",
                        "citation": f"ChEMBL: {molecule.get('chembl_id')} - Phase {molecule.get('max_phase', 'N/A')}",
                        "url": molecule.get("url", ""),
                        "relevance_score": 0.75,
                        "quality_score": 0.9,
                        "key_findings": [f"Clinical Phase: {molecule.get('max_phase', 'Preclinical')}"],
                        "excerpts": []
                    })
                
                logger.success(f"Found {len(chembl_results)} ChEMBL molecules")
                
            except Exception as e:
                logger.error(f"ChEMBL search failed: {str(e)}")
        
        # 9. Search Zenodo for datasets
        try:
            zenodo_results = await self.zenodo.search(
                query=main_query,
                max_results=5
            )
            
            for resource in zenodo_results:
                evidence_packs.append({
                    "source": "Zenodo",
                    "title": resource.get("title", ""),
                    "citation": resource.get("citation", ""),
                    "url": resource.get("url", ""),
                    "relevance_score": 0.6,
                    "quality_score": 0.7,
                    "key_findings": resource.get("key_findings", []),
                    "excerpts": [],
                    "epistemic_metadata": {}  # Zenodo datasets lack structured epistemic metadata
                })
            
            logger.success(f"Found {len(zenodo_results)} Zenodo resources")
            
        except Exception as e:
            logger.error(f"Zenodo search failed: {str(e)}")
        
        # 10. Search Kaggle for datasets (if configured)
        try:
            if self.kaggle._is_configured():
                # Use simpler, broader search terms for Kaggle
                # Kaggle works better with domain names and general terms
                kaggle_query = domain if domain not in ["general", "multidomain"] else research_goal.split()[0]
                
                # Try to extract key medical terms from search_terms
                medical_keywords = []
                for term in search_terms[:5]:
                    term_lower = term.lower()
                    # Look for disease/condition terms
                    if any(kw in term_lower for kw in ["disease", "diabetes", "cancer", "cardiac", "neural", "infection"]):
                        medical_keywords.append(term)
                
                # Combine domain with key medical term if available
                if medical_keywords:
                    kaggle_query = f"{domain} {medical_keywords[0]}"
                
                kaggle_results = await self.kaggle.search_datasets(
                    query=kaggle_query,
                    tags=["medicine", "biology", "healthcare"],
                    max_results=5
                )
                
                for dataset in kaggle_results:
                    evidence_packs.append({
                        "source": "Kaggle",
                        "title": dataset.get("title", ""),
                        "citation": f"Kaggle: {dataset.get('creator_name')} - {dataset.get('downloads')} downloads",
                        "url": dataset.get("url", ""),
                        "relevance_score": 0.65,
                        "quality_score": 0.75,
                        "key_findings": [f"{dataset.get('file_count')} files, {dataset.get('votes')} votes"],
                        "excerpts": [dataset.get("subtitle", "")[:300]],
                        "epistemic_metadata": {}  # Kaggle datasets lack structured epistemic metadata
                    })
                
                logger.success(f"Found {len(kaggle_results)} Kaggle datasets")
        except Exception as e:
            logger.error(f"Kaggle search failed: {str(e)}")
        
        # === INTELLIGENCE LAYER: Enhanced Processing ===
        logger.info(f"Applying intelligence layer to {len(evidence_packs)} raw evidence packs...")
        
        # 1. Smart Deduplication
        evidence_packs = self.deduplicator.deduplicate(
            evidence_packs,
            keep_highest_quality=True
        )
        logger.info(f"After deduplication: {len(evidence_packs)} unique evidence packs")

        # 2. Domain-Specific Relevance Boosting (Nobel 3.0 LITE Enhancement)
        # Extract target concepts from concept map for domain-aware scoring
        target_concepts = self._extract_target_concepts_for_relevance(concept_map, goal)
        domain_context = f"{domain}:{goal[:50]}" if goal else domain
        
        logger.info(f"Applying domain-specific relevance scoring with {len(target_concepts)} target concepts")
        
        # Apply relevance boost before comprehensive scoring
        for evidence in evidence_packs:
            relevance_boost = self._calculate_domain_relevance(
                evidence, target_concepts, domain_context
            )
            # Store relevance as metadata
            evidence["domain_relevance"] = round(relevance_boost, 3)

        # 3. Apply enhanced scoring and tier classification
        # NOTE: Epistemic metadata MUST come from connectors (PubMed, ClinicalTrials)
        # NO FALLBACK extraction - medical applications require validated metadata
        for evidence in evidence_packs:
            scores = self.scorer.calculate_comprehensive_score(
                evidence=evidence,
                query_terms=search_terms,
                domain=domain
            )
            # Update evidence with enhanced scores
            evidence.update(scores)
            
            # Blend domain relevance into confidence score (30% weight)
            original_confidence = scores.get("confidence_score", 0.5)
            domain_relevance = evidence.get("domain_relevance", 0.5)
            evidence["confidence_score"] = round(
                0.70 * original_confidence + 0.30 * domain_relevance,
                3
            )
            
            # Add evidence tier classification
            evidence["evidence_tier"] = self.scorer.get_evidence_tier(evidence["confidence_score"])
        
        logger.info("Applied enhanced scoring with domain-specific relevance boosting")
        
        # Rank evidence by confidence score
        evidence_packs = self.scorer.rank_evidence_packs(evidence_packs)
        
        # Use AI to enhance evidence packs with key findings
        evidence_packs = await self._enhance_evidence_packs(evidence_packs, concept_map, goal)

        
        # 5. Log quality statistics
        tiers = {}
        for evidence in evidence_packs:
            tier = evidence.get("evidence_tier", "UNKNOWN")
            tiers[tier] = tiers.get(tier, 0) + 1
        
        logger.success(f"Compiled {len(evidence_packs)} evidence packs with quality tiers: {tiers}")
        logger.info(f"Top evidence: {evidence_packs[0].get('title', '')[:60]}... (confidence: {evidence_packs[0].get('confidence_score', 0):.2f})")
        
        return evidence_packs
    
    def _extract_search_terms(self, concept_map: Dict[str, Any], goal: str) -> List[str]:
        """Extract relevant search terms from concept map"""
        terms = set()
        
        # Add terms from concepts
        for concept in concept_map.get("concepts", []):
            terms.add(concept.get("term", ""))
            terms.update(concept.get("targets", []))
        
        # Add pathway names
        for pathway in concept_map.get("key_pathways", []):
            terms.add(pathway.get("name", ""))
        
        # Remove empty strings
        terms.discard("")
        
        return list(terms)
    
    def _extract_target_concepts_for_relevance(self, concept_map: Dict[str, Any], goal: str) -> List[str]:
        """
        Extract target concepts for domain-specific relevance scoring.
        
        Returns key concepts that should be matched in evidence abstracts/titles
        for relevance boosting (e.g., glioblastoma, CAR-T, BBB, nanoparticles).
        """
        concepts = []
        
        # Extract from concept map
        for concept in concept_map.get("concepts", [])[:15]:  # Top 15 concepts
            term = concept.get("term", "").strip()
            if term and len(term) > 3:
                concepts.append(term.lower())
        
        # Extract from goal (key medical terms)
        if goal:
            # Simple tokenization - extract meaningful terms
            stopwords = {"the", "and", "for", "with", "using", "novel", "enhanced", 
                        "therapy", "treatment", "approach", "this", "that", "will"}
            goal_terms = [
                w.strip(".,;:()[]") 
                for w in goal.lower().split() 
                if len(w) > 4 and w not in stopwords
            ]
            concepts.extend(goal_terms[:10])  # Top 10 from goal
        
        # Deduplicate
        return list(set(concepts))
    
    def _calculate_domain_relevance(
        self, 
        evidence: Dict[str, Any], 
        target_concepts: List[str], 
        domain_context: str
    ) -> float:
        """
        Calculate domain-specific relevance score.
        
        Boosts evidence that matches target concepts and domain context.
        De-boosts off-context evidence (e.g., vascular TfR for brain delivery).
        """
        title = evidence.get("title", "").lower()
        abstract = evidence.get("abstract", "").lower()
        journal = evidence.get("venue", evidence.get("journal", "")).lower()
        text = f"{title} {abstract} {journal}"
        
        # Base score
        score = 0.5
        
        # Concept matching (0-0.3)
        concept_hits = sum(1 for concept in target_concepts if concept in text)
        if target_concepts:
            concept_coverage = concept_hits / len(target_concepts)
            score += concept_coverage * 0.3
        
        # Domain-specific boosts
        domain_lower = domain_context.lower()
        
        # GBM/Brain context
        if any(term in domain_lower for term in ["glioblastoma", "gbm", "brain", "neuro"]):
            if any(term in text for term in ["glioblastoma", "gbm", "brain tumor", "malignant glioma"]):
                score += 0.15
            if any(term in text for term in ["egfrviii", "il13ra2", "her2", "epha2"]):
                score += 0.10
        
        # CAR-T context
        if any(term in domain_lower for term in ["car-t", "immunotherapy"]):
            if any(term in text for term in ["car-t", "chimeric antigen receptor"]):
                score += 0.15
            if any(term in text for term in ["solid tumor", "persistence", "exhaustion"]):
                score += 0.08
        
        # BBB/CNS delivery context
        if any(term in domain_lower for term in ["bbb", "blood-brain", "delivery"]):
            if any(term in text for term in ["blood-brain barrier", "bbb"]):
                score += 0.15
            if any(term in text for term in ["focused ultrasound", "transcytosis"]):
                score += 0.10
        
        # Nanoparticle context
        if "nanoparticle" in domain_lower or "nano" in domain_lower:
            if any(term in text for term in ["nanoparticle", "lipid nanoparticle", "lnp"]):
                score += 0.10
        
        # De-boost off-context evidence
        # Example: TfR studies without brain/CNS context
        if "transferrin receptor" in text or "tfr" in text:
            if not any(term in text for term in ["brain", "cns", "bbb", "glioblastoma", "neural"]):
                score -= 0.15  # Vascular/systemic TfR less relevant for brain delivery
        
        # Ensure [0, 1]
        return max(0.0, min(1.0, score))
    
    async def _enhance_evidence_packs(
        self,
        evidence_packs: List[Dict[str, Any]],
        concept_map: Dict[str, Any],
        goal: str
    ) -> List[Dict[str, Any]]:
        """Use AI to extract key findings from evidence"""
        
        if not evidence_packs:
            return evidence_packs
        
        try:
            # Process in batches to avoid overwhelming the API
            for i, pack in enumerate(evidence_packs[:10]):  # Limit to first 10
                if not pack.get("key_findings"):
                    title = pack.get("title", "")
                    
                    prompt = f"""Based on this research title and the medical goal, extract 2-3 key findings or insights:

Title: {title}

Medical Goal: {goal}

Provide key findings as a JSON array of strings:
{{"key_findings": ["finding1", "finding2", "finding3"]}}"""
                    
                    try:
                        result = await deepseek_client.generate_json(
                            prompt=prompt,
                            temperature=0.3,
                            max_tokens=300
                        )
                        
                        pack["key_findings"] = result.get("key_findings", [])
                        
                    except Exception as e:
                        logger.debug(f"Failed to enhance evidence pack {i}: {str(e)}")
                        continue
            
        except Exception as e:
            logger.error(f"Error enhancing evidence packs: {str(e)}")
        
        return evidence_packs
