# 🧠 Medical Discovery & Hypothesis Engine
## Nobel-Level AI Research Co-Creator

> **Version:** 1.0.0-Intelligence  
> **Status:** Production-Ready with Enhanced Intelligence Layer  
> **Mission:** Transform medical research through AI-powered hypothesis generation with deep reasoning

---

## 🎯 **Core Vision**

This system is not just an answer machine—it's a **cognitive research ecosystem** that:
- **Envisions** rather than answers
- **Discovers** cross-domain innovations
- **Validates** through simulation
- **Learns** from experimental outcomes
- **Reasons** transparently with full provenance

---

## 🚀 **Key Features**

### **1. Multi-Agent Intelligence**
7 specialized AI agents working in orchestrated pipeline:
- **Visioner Agent**: Generates novel research directions
- **Concept Learner**: Builds semantic concept maps
- **Evidence Miner**: Gathers & scores evidence from 10 sources
- **Cross-Domain Mapper**: Finds analogies from other fields
- **Synthesizer**: Creates comprehensive hypothesis documents
- **Simulation Agent**: Assesses scientific feasibility
- **Ethics Validator**: Ensures ethical compliance

### **2. Enhanced Evidence Intelligence** 🆕 
**Nobel-level evidence processing:**

#### **Intelligent Query Expansion**
- Medical synonym expansion (diabetes → T2DM, hyperglycemia, glucose intolerance)
- Ontology-based term enrichment (MeSH-style)
- Acronym resolution (AMR → antimicrobial resistance)
- Domain-specific keyword injection
- Multi-strategy queries per data source type

#### **Advanced Evidence Scoring**
Multi-dimensional scoring system:
- **Relevance Score** (0-1): Term matching + semantic similarity
- **Quality Score** (0-1): Source credibility + peer-review status + journal impact
- **Recency Score** (0-1): Exponential decay (5-year half-life)
- **Impact Score** (0-1): Citations + downloads + usage metrics
- **Confidence Score** (0-1): Weighted combination of all dimensions

**Evidence Tier Classification:**
- TIER_1_EXCEPTIONAL (≥0.85)
- TIER_2_HIGH (≥0.75)
- TIER_3_MODERATE (≥0.60)
- TIER_4_LOW (≥0.45)
- TIER_5_MARGINAL (<0.45)

#### **Smart Deduplication**
- Exact matching via DOI/PMID/NCT ID/arXiv ID
- Fuzzy title matching (85% similarity threshold)
- Cross-source evidence linking
- Quality-based duplicate resolution (keeps highest quality)
- Evidence merging (combines information from duplicates)

#### **Provenance & Transparency**
- Complete reasoning chains for all decisions
- Source attribution for every evidence piece
- Confidence intervals and uncertainty quantification
- Quality tier justification

### **3. Comprehensive Data Integration**
**10 Scientific Data Sources:**

| Source | Type | API | Data |
|--------|------|-----|------|
| **PubMed** | Publications | Free | 35M+ peer-reviewed articles |
| **Crossref** | Publications | Free | 150M+ DOI records |
| **arXiv** | Preprints | Free | 2M+ preprints (q-bio) |
| **ClinicalTrials.gov** | Clinical | Free | 450K+ clinical trials |
| **UniProt** | Proteins | Free | 250M+ protein sequences |
| **KEGG** | Pathways | Free | 500+ human pathways |
| **PubChem** | Chemistry | Free | 110M+ compounds |
| **ChEMBL** | Bioactivity | Free | 2M+ compounds, 1M+ assays |
| **Zenodo** | Datasets | Free | 6M+ research datasets |
| **Kaggle** | Datasets | Credentials | 50K+ datasets |

**Smart Source-Specific Query Optimization:**
- Literature (PubMed/Crossref/arXiv): Natural language + synonyms
- Proteins (UniProt): Gene/protein names + functional terms
- Pathways (KEGG): Broad metabolic terms (insulin, glucose)
- Datasets (Kaggle/Zenodo): Domain + key medical term

### **4. Medical Domain Coverage**
- **Diabetes** (insulin, glucose, metabolic)
- **Cardiology** (heart, vascular, coronary)
- **Oncology** (cancer, tumor, chemotherapy)
- **Neurology** (brain, cognitive, neural)
- **Immunology** (immune, antibody, cytokine)
- **Infectious Diseases** (pathogen, antimicrobial, vaccine)
- **And 9 more domains...**

### **5. Production-Grade Architecture**
- **FastAPI** with async/await throughout
- **MongoDB** for persistence with in-memory fallback
- **DeepSeek AI** (deepseek-chat) for all agents
- **Pydantic** for data validation
- **Comprehensive error handling** with JSON serialization
- **Loguru** for structured logging
- **Health checks** for API + MongoDB

---

## 📊 **Intelligence Layer Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                     USER RESEARCH QUERY                      │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                   ORCHESTRATOR (7-Step Pipeline)             │
├─────────────────────────────────────────────────────────────┤
│  Step 1: Visioner Agent → Generate Directions               │
│  Step 2: Concept Learner → Build Concept Map                │
│  Step 3: Evidence Miner → Gather & Score Evidence 🆕        │
│           ├─ Query Expansion (synonyms, ontology)           │
│           ├─ Multi-source search (10 connectors)            │
│           ├─ Smart Deduplication (DOI/fuzzy matching)       │
│           ├─ Enhanced Scoring (5D: R+Q+R+I+C)               │
│           └─ Evidence Ranking (by confidence)               │
│  Step 4: Cross-Domain Mapper → Find Transfers               │
│  Step 5: Synthesizer → Create Hypothesis Document           │
│  Step 6: Simulation Agent → Assess Feasibility              │
│  Step 7: Ethics Validator → Validate Ethics                 │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│         HYPOTHESIS (with provenance & tier classification)   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ **Installation & Setup**

### **Prerequisites**
- Python 3.12+
- MongoDB (local or remote)
- DeepSeek API Key

### **1. Install Dependencies**
```powershell
pip install -r requirements.txt
```

### **2. Configure Environment**
Create `.env` file:
```env
# API Keys
DEEPSEEK_API_KEY=your_deepseek_api_key_here
PUBMED_API_KEY=optional_pubmed_api_key

# MongoDB
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=medresearch

# Server
API_HOST=localhost
API_PORT=8000
DEBUG=False
```

### **3. Configure Kaggle (Optional)**
Create `kaggle.json` in project root:
```json
{
  "username": "your_kaggle_username",
  "key": "your_kaggle_api_key"
}
```

### **4. Start MongoDB**
```powershell
# If using local MongoDB
mongod --dbpath C:\data\db
```

### **5. Run Server**
```powershell
python run.py
```

Server starts at: `http://localhost:8000`

---

## 📚 **API Usage**

### **Health Check**
```bash
GET /health
```

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "mongodb_connected": true,
  "intelligence_modules": ["EvidenceScorer", "QueryExpander", "EvidenceDeduplicator"]
}
```

### **Create Hypothesis**
```bash
POST /v1/hypotheses
```

**Request Body:**
```json
{
  "research_goal": "Discover novel therapeutic targets for type 2 diabetes using multi-omics approaches",
  "domain": "diabetes",
  "constraints": {
    "focus_areas": ["insulin resistance", "beta cell function", "metabolomics"],
    "avoid_areas": ["surgical interventions"],
    "timeline": "5 years"
  }
}
```

**Response:**
```json
{
  "id": "hyp_abc123def456",
  "status": "pending",
  "message": "Hypothesis generation started. Use GET /v1/hypotheses/{id} to check status."
}
```

### **Get Hypothesis**
```bash
GET /v1/hypotheses/{hypothesis_id}
```

**Response (completed):**
```json
{
  "id": "hyp_abc123def456",
  "status": "completed",
  "research_goal": "...",
  "domain": "diabetes",
  "hypothesis_directions": [...],
  "concept_map": {
    "concepts": [...],
    "relationships": [...]
  },
  "evidence_packs": [
    {
      "source": "PubMed",
      "title": "...",
      "citation": "...",
      "url": "...",
      "relevance_score": 0.92,
      "quality_score": 0.95,
      "recency_score": 0.88,
      "impact_score": 0.85,
      "confidence_score": 0.91,
      "evidence_tier": "TIER_1_EXCEPTIONAL",
      "key_findings": [...],
      "excerpts": [...]
    }
  ],
  "hypothesis_document": {
    "title": "...",
    "abstract": "...",
    "rationale": "...",
    "methodology": "...",
    "expected_outcomes": "...",
    "novelty_score": 0.88
  },
  "cross_domain_transfers": [...],
  "simulation_scorecard": {
    "overall_feasibility": "GREEN",
    "scores": {...}
  },
  "ethics_report": {
    "verdict": "GREEN",
    "considerations": [...]
  },
  "provenance": [...]
}
```

---

## 🧪 **Testing**

### **Run Comprehensive Test**
```powershell
python test_hypothesis.py
```

**Test covers:**
1. Health check (API + MongoDB)
2. Hypothesis creation
3. Status monitoring
4. Completion verification
5. Evidence quality analysis

### **Expected Results**
- **Evidence Sources**: 8-10 sources active (depends on Kaggle config)
- **Evidence Packs**: 55-70 (after deduplication)
- **Evidence Tiers**: 
  - TIER_1: 10-15%
  - TIER_2: 25-35%
  - TIER_3: 30-40%
  - TIER_4+5: 20-25%
- **Processing Time**: 5-8 minutes (7 agents + 10 sources)

---

## 🔬 **Evidence Quality Improvements**

### **Before Intelligence Layer**
```
PubMed: 15 | Crossref: 10 | arXiv: 0 (error) | ClinicalTrials: 10
UniProt: 5 | KEGG: 0 | Zenodo: 5 | Kaggle: 0
Total: 45 raw evidence packs
Issues: Duplicates, 301 errors, poor relevance, no quality ranking
```

### **After Intelligence Layer** 🆕
```
PubMed: 15 | Crossref: 10 | arXiv: 5-10 | ClinicalTrials: 10
UniProt: 5 | KEGG: 3-5 | Zenodo: 5 | Kaggle: 2-5
Total: 55-65 unique evidence packs (after smart deduplication)
Quality: 5D scoring, tier classification, ranked by confidence
Improvements:
  ✅ +22% more evidence (fixed arXiv, KEGG, Kaggle)
  ✅ Smart deduplication (DOI/PMID/fuzzy matching)
  ✅ Enhanced scoring (relevance, quality, recency, impact)
  ✅ Evidence ranking (best evidence first)
  ✅ Tier classification (EXCEPTIONAL to MARGINAL)
  ✅ Query expansion (medical synonyms, ontology)
```

---

## 🎓 **Medical Ontology & Synonyms**

System includes comprehensive medical terminology:

### **Example Expansions**
- `diabetes` → diabetes mellitus, diabetic, hyperglycemia, glucose intolerance, T2D, T2DM, NIDDM
- `heart failure` → cardiac failure, HF, CHF, congestive heart failure
- `cancer` → carcinoma, tumor, malignancy, neoplasm, oncology
- `insulin` → insulin hormone, insulin secretion, insulin resistance

### **Acronym Support**
- AMR, T2D, T1D, CVD, CHD, COPD, HIV, AIDS, DNA, RNA, mRNA, PCR, MRI, CT, PET, FDA, NIH, WHO

---

## 📈 **Roadmap: Next-Level Intelligence**

### **Phase 1: Enhanced Reasoning** (1-2 months)
- [ ] Neo4j Knowledge Graph integration
- [ ] Import MeSH, GO, DOID ontologies
- [ ] Causal relationship modeling
- [ ] Pathway reconstruction
- [ ] Patent search (USPTO/EPO)

### **Phase 2: Validation Layer** (2-3 months)
- [ ] RDKit for chemical structure analysis
- [ ] AutoDock Vina for molecular docking
- [ ] QSAR model training
- [ ] SBML systems biology modeling
- [ ] COPASI pathway simulation

### **Phase 3: Learning & Adaptation** (3-4 months)
- [ ] Feedback loop for experimental results
- [ ] Pattern recognition across hypotheses
- [ ] Agent behavior adaptation
- [ ] Meta-analysis capabilities
- [ ] Confidence calibration

---

## 🏆 **Current Achievements**

✅ **Production-ready system** with 7 agents + 10 data connectors  
✅ **Intelligence layer** with scoring, expansion, deduplication  
✅ **MongoDB persistence** with in-memory fallback  
✅ **Comprehensive error handling** and logging  
✅ **Smart query optimization** per data source  
✅ **Evidence tier classification** for quality assurance  
✅ **Full provenance tracking** for transparency  
✅ **Bug fixes**: arXiv HTTPS, KEGG pathways, Kaggle datasets  

---

## 👥 **Contributing**

This is a research-grade tool designed for **Nobel-level innovation**. 

For questions or contributions, focus on:
- Enhanced reasoning capabilities
- Additional data sources
- Improved ontology integration
- Validation simulations
- Meta-learning mechanisms

---

## 📄 **License**

Research & Educational Use

---

## 🌟 **Vision Statement**

> "We're not building AI that answers questions.  
> We're building AI that **envisions futures** medical research hasn't discovered yet."

**From concept to validation in 7 AI-powered steps.**

---

## 📞 **Support**

- **Documentation**: See `/docs` folder
- **API Reference**: `http://localhost:8000/docs` (FastAPI auto-generated)
- **Logs**: `logs/` directory with structured logging
- **Issues**: Track in `FIXES_APPLIED.md`

---

**Built with ❤️ for advancing medical research through AI**
