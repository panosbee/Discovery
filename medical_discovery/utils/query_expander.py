"""
Intelligent Query Expansion

Expands search queries with:
- Medical synonyms and related terms
- Ontology-based term expansion (MeSH-style)
- Domain-specific keywords
- Acronym expansion
"""

from typing import List, Set, Dict, Any, Optional
from loguru import logger


class QueryExpander:
    """
    Intelligent query expansion for medical research
    """
    
    def __init__(self):
        # Medical synonym dictionary (expandable)
        self.medical_synonyms = {
            # Diabetes-related
            "diabetes": ["diabetes mellitus", "diabetic", "hyperglycemia", "glucose intolerance"],
            "insulin": ["insulin hormone", "insulin secretion", "insulin resistance"],
            "glucose": ["blood glucose", "blood sugar", "glycemia", "dextrose"],
            "type 2 diabetes": ["T2D", "T2DM", "NIDDM", "non-insulin dependent diabetes"],
            "type 1 diabetes": ["T1D", "T1DM", "IDDM", "insulin dependent diabetes"],
            
            # Cardiovascular
            "heart": ["cardiac", "cardiovascular", "myocardial"],
            "heart failure": ["cardiac failure", "HF", "CHF", "congestive heart failure"],
            "hypertension": ["high blood pressure", "HTN", "elevated blood pressure"],
            "stroke": ["cerebrovascular accident", "CVA", "brain attack"],
            
            # Cancer
            "cancer": ["carcinoma", "tumor", "malignancy", "neoplasm", "oncology"],
            "chemotherapy": ["chemo", "cytotoxic therapy", "cancer treatment"],
            "metastasis": ["metastatic", "spread", "secondary cancer"],
            
            # Neurological
            "alzheimer": ["AD", "alzheimer disease", "dementia"],
            "parkinson": ["PD", "parkinson disease", "parkinsonian"],
            "epilepsy": ["seizure disorder", "convulsions"],
            
            # Immunological
            "immune": ["immunity", "immunological", "immune system"],
            "antibody": ["immunoglobulin", "Ig", "antibodies"],
            "inflammation": ["inflammatory", "inflamed"],
            
            # General medical
            "treatment": ["therapy", "intervention", "therapeutic"],
            "drug": ["medication", "pharmaceutical", "medicine"],
            "protein": ["polypeptide", "peptide"],
            "gene": ["genetic", "genome", "genomic"],
            "pathway": ["signaling pathway", "metabolic pathway", "cellular pathway"],
        }
        
        # Domain-specific keyword enrichment
        self.domain_keywords = {
            "diabetes": [
                "insulin", "glucose", "pancreas", "beta cell", "metabolic",
                "glycemic control", "HbA1c", "glucagon", "GLP-1"
            ],
            "cardiology": [
                "heart", "cardiac", "vascular", "blood pressure", "coronary",
                "artery", "ECG", "echocardiogram", "myocardial"
            ],
            "oncology": [
                "cancer", "tumor", "malignant", "metastasis", "chemotherapy",
                "radiation", "oncogene", "apoptosis", "proliferation"
            ],
            "neurology": [
                "brain", "neural", "neuron", "cognitive", "neurological",
                "CNS", "neurotransmitter", "synaptic"
            ],
            "immunology": [
                "immune", "antibody", "T cell", "B cell", "cytokine",
                "inflammation", "autoimmune", "immunotherapy"
            ],
            "infectious_diseases": [
                "infection", "pathogen", "bacteria", "virus", "antimicrobial",
                "antibiotic", "resistance", "vaccine"
            ],
        }
        
        # Common medical acronyms
        self.acronym_expansions = {
            "AMR": "antimicrobial resistance",
            "T2D": "type 2 diabetes",
            "T1D": "type 1 diabetes",
            "CVD": "cardiovascular disease",
            "CHD": "coronary heart disease",
            "COPD": "chronic obstructive pulmonary disease",
            "HIV": "human immunodeficiency virus",
            "AIDS": "acquired immunodeficiency syndrome",
            "DNA": "deoxyribonucleic acid",
            "RNA": "ribonucleic acid",
            "mRNA": "messenger RNA",
            "PCR": "polymerase chain reaction",
            "MRI": "magnetic resonance imaging",
            "CT": "computed tomography",
            "PET": "positron emission tomography",
            "FDA": "food and drug administration",
            "NIH": "national institutes of health",
            "WHO": "world health organization",
        }
    
    def expand_query(
        self,
        query: str,
        domain: Optional[str] = None,
        max_terms: int = 10,
        include_synonyms: bool = True,
        include_domain_keywords: bool = True,
        include_acronyms: bool = True
    ) -> List[str]:
        """
        Expand query with related terms
        
        Args:
            query: Original search query
            domain: Medical domain for domain-specific expansion
            max_terms: Maximum number of expanded terms to return
            include_synonyms: Include medical synonyms
            include_domain_keywords: Include domain-specific keywords
            include_acronyms: Expand acronyms
            
        Returns:
            List of expanded query terms
        """
        expanded_terms: Set[str] = set()
        query_lower = query.lower()
        
        # Add original query
        expanded_terms.add(query)
        
        # 1. Synonym expansion
        if include_synonyms:
            for base_term, synonyms in self.medical_synonyms.items():
                if base_term in query_lower:
                    expanded_terms.update(synonyms[:3])  # Add top 3 synonyms
        
        # 2. Domain-specific keywords
        if include_domain_keywords and domain:
            domain_key = domain.lower()
            if domain_key in self.domain_keywords:
                # Add domain keywords that relate to query
                domain_terms = self.domain_keywords[domain_key]
                # Smart selection: only add if somewhat related
                for term in domain_terms[:5]:
                    # Add if term appears in query or its synonyms
                    if term.lower() in query_lower:
                        expanded_terms.add(term)
        
        # 3. Acronym expansion
        if include_acronyms:
            words = query.split()
            for word in words:
                word_upper = word.upper().strip(".,;:")
                if word_upper in self.acronym_expansions:
                    expanded_terms.add(self.acronym_expansions[word_upper])
        
        # 4. Extract key medical concepts from query
        medical_concepts = self._extract_medical_concepts(query)
        expanded_terms.update(medical_concepts[:3])
        
        # Limit to max_terms
        result = list(expanded_terms)[:max_terms]
        
        logger.debug(f"Expanded query '{query}' to {len(result)} terms")
        return result
    
    def _extract_medical_concepts(self, query: str) -> List[str]:
        """
        Extract key medical concepts from query using pattern matching
        """
        concepts = []
        query_lower = query.lower()
        
        # Pattern: "X receptor", "X pathway", "X signaling"
        import re
        
        # Receptor patterns
        receptor_match = re.findall(r'(\w+)\s+receptor', query_lower)
        concepts.extend([f"{r} receptor" for r in receptor_match])
        
        # Pathway patterns
        pathway_match = re.findall(r'(\w+)\s+pathway', query_lower)
        concepts.extend([f"{p} pathway" for p in pathway_match])
        
        # Signaling patterns
        signaling_match = re.findall(r'(\w+)\s+signaling', query_lower)
        concepts.extend([f"{s} signaling" for s in signaling_match])
        
        # Disease patterns
        disease_keywords = ["disease", "syndrome", "disorder", "condition"]
        for keyword in disease_keywords:
            disease_match = re.findall(rf'(\w+)\s+{keyword}', query_lower)
            concepts.extend([f"{d} {keyword}" for d in disease_match])
        
        return concepts
    
    def create_multi_query_strategy(
        self,
        research_goal: str,
        domain: str,
        concepts: List[str]
    ) -> Dict[str, List[str]]:
        """
        Create multiple query strategies for different data sources
        
        Returns:
            Dict mapping source type to optimized queries
        """
        strategies = {}
        
        # Strategy 1: Broad queries for literature databases (PubMed, Crossref, arXiv)
        literature_terms = self.expand_query(
            research_goal,
            domain=domain,
            max_terms=8,
            include_synonyms=True
        )
        strategies["literature"] = literature_terms
        
        # Strategy 2: Specific queries for protein/gene databases (UniProt)
        protein_terms = [
            c for c in concepts
            if any(kw in c.lower() for kw in ["protein", "receptor", "enzyme", "kinase", "gene"])
        ]
        if protein_terms:
            strategies["protein"] = protein_terms[:5]
        else:
            strategies["protein"] = [research_goal]
        
        # Strategy 3: Pathway queries for KEGG
        pathway_terms = []
        for concept in concepts[:5]:
            if any(kw in concept.lower() for kw in ["pathway", "signaling", "metabolism"]):
                pathway_terms.append(concept)
        
        # Add domain-specific pathway terms
        if domain in self.domain_keywords:
            pathway_terms.extend([
                t for t in self.domain_keywords[domain]
                if any(kw in t.lower() for kw in ["pathway", "signaling"])
            ][:2])
        
        strategies["pathway"] = pathway_terms if pathway_terms else [domain, "metabolism"]
        
        # Strategy 4: Simple queries for dataset repositories (Kaggle, Zenodo)
        dataset_terms = [domain]
        # Add 1-2 key concepts
        dataset_terms.extend([c for c in concepts if len(c.split()) <= 2][:2])
        strategies["dataset"] = dataset_terms
        
        # Strategy 5: Chemical/drug queries for PubChem/ChEMBL
        chem_terms = [
            c for c in concepts
            if any(kw in c.lower() for kw in ["drug", "compound", "molecule", "inhibitor", "agonist"])
        ]
        if not chem_terms:
            chem_terms = [f"{domain} drug", f"{domain} therapeutic"]
        strategies["chemical"] = chem_terms[:5]
        
        logger.info(f"Created {len(strategies)} query strategies with {sum(len(v) for v in strategies.values())} total terms")
        return strategies
    
    def optimize_query_for_source(
        self,
        query: str,
        source: str,
        domain: Optional[str] = None
    ) -> str:
        """
        Optimize query for specific data source
        """
        query_lower = query.lower()
        
        if source == "KEGG":
            # KEGG prefers single broad terms
            # Extract first meaningful term
            words = [w for w in query.split() if len(w) > 3]
            return words[0] if words else domain or "metabolism"
        
        elif source == "Kaggle":
            # Kaggle works best with domain + one key term
            if domain and domain not in query_lower:
                return f"{domain} {query.split()[0]}"
            return query.split()[0] if query else domain
        
        elif source in ["arXiv", "Crossref"]:
            # These work well with natural language queries
            return query
        
        elif source == "UniProt":
            # UniProt works well with protein/gene names
            return query
        
        else:
            return query
