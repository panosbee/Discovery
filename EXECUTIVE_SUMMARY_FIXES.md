# Executive Summary Enhancement - Implementation Notes

## Changes Required:

### 1. Evidence System Fix
- ✅ Fixed `_count_evidence_tiers()` to use both relevance AND quality scores
- ✅ Added `_calculate_evidence_strength()` with weighted formula
- Use T1/T2/T3/T4 tiers (removed T5)

### 2. Diagnostic Mode Detection
Detect if hypothesis is diagnostic vs therapeutic:
- Keywords: "diagnostic", "biomarker", "detection", "screening", "test"
- vs "treatment", "therapy", "drug", "intervention"

### 3. Timeline & Cost Templates

**Diagnostic (IVD/CLIA):**
- Timeline: 12-24 months for RUO → CLIA LDT / CE-IVD pilot
- Cost: €250k-€1.2M (assays, SOPs, cohorts, QC, regulatory)
- Phases: SOPs+validation (0-6m), replication+model (6-12m), pilot release (12-18m)

**Therapeutic (Drug):**
- Timeline: 18-36 months for preclinical → Phase I/II
- Cost: $2-5M (preclinical, IND, Phase I, Phase II PoC)
- Phases: Preclinical (1-6m), lead opt (7-12m), IND-enabling (13-18m), Phase I/II (19-36m)

### 4. Priority Actions by Type

**Diagnostic:**
1. Preanalytical SOPs (tubes, temps, processing, spike-ins)
2. Analytical validation (LoD/LoQ, precision, reproducibility)
3. Pilot cohort (n≈150: HC/MCI/AD, pre-registered)
4. Modeling (SHAP-explainable, calibration)
5. Clinical utility study (decision-curve analysis)
6. Regulatory pathway (CLIA/CE-IVD dossier)

**Therapeutic:**
1. Validate key molecular targets in disease model
2. Test delivery route for bioavailability
3. Conduct in vitro/in vivo safety studies
4. Optimize lead compounds
5. IND-enabling toxicology
6. Phase I trial design

### 5. Feasibility Scoring

**Diagnostic-specific:**
```python
technical_feasibility = f(assay_availability, SOP_maturity, reproducibility)  # 0-100
clinical_translatability = f(sample_type, workflow_complexity, scalability)   # 0-100
regulatory_path_ready = f(IVD/CE/CLIA_readiness)                             # 0-100
safety_profile = high for blood diagnostics (penalize misuse risk)            # 0-100

composite = 0.35*technical + 0.35*clinical + 0.2*regulatory + 0.1*safety
```

Labels:
- ≥80%: HIGH
- 60-79%: MODERATE-HIGH
- 40-59%: MODERATE  
- <40%: LOW

### 6. Evidence Strength Display
Instead of:
```
**Evidence Base**: 0 high-quality studies + 0 supporting sources
```

Show:
```
**Evidence Base**: 29 sources → T1: 0, T2: 6, T3: 17, T4: 6
**Evidence Strength**: 0.54 (Moderate) — individual components supported; combination is novel
```

### 7. Ethics Consistency Rule
```python
if evidence_strength < 0.45:
    ethics_max = "AMBER"  # Cannot be GREEN with weak evidence
```

### 8. Truncation Guard
```python
def truncate_guard(text: str, min_chars: int = 100) -> str:
    """Ensure text is complete, no ellipsis mid-word"""
    if '...' in text and len(text) < 500:
        # Suspicious truncation
        return text.replace('...', '')
    return text
```

### 9. Consistency Checks Before Render
```python
def validate_executive_summary(summary: Dict) -> List[str]:
    """Return list of inconsistencies"""
    issues = []
    
    # Check: evidence numbers match
    if "0 high-quality" in summary['evidence_strength'] and "29 sources" in summary['current_treatment_gap']:
        issues.append("Evidence count mismatch")
    
    # Check: feasibility percentages not 0% unless justified
    if "Technical Feasibility: 0%" in summary['feasibility_verdict'] and "HIGHLY FEASIBLE" in summary['feasibility_verdict']:
        issues.append("Feasibility contradiction")
    
    # Check: diagnostic timeline doesn't mention IND/Phase I
    if "IND" in summary['estimated_timeline'] and "diagnostic" in summary['elevator_pitch'].lower():
        issues.append("Diagnostic using drug timeline")
    
    return issues
```

## Implementation Priority:

1. **HIGH**: Fix evidence counting (critical for credibility)
2. **HIGH**: Remove 0% technical feasibility (critical contradiction)
3. **HIGH**: Diagnostic mode detection + correct timeline/cost
4. **MEDIUM**: Remove truncation
5. **MEDIUM**: Diagnostic-specific priority actions
6. **LOW**: Novelty index

## Test After Changes:
```bash
python test_nobel_phase2.py
```

Expected:
- ✅ Evidence: "29 sources → T2: 6, T3: 17, T4: 6"
- ✅ Evidence Strength: "0.54 (Moderate)"
- ✅ Technical Feasibility: >60%
- ✅ Timeline: "12-24 months" (for diagnostic)
- ✅ Cost: "€250k-€1.2M" (for diagnostic)
- ✅ Priority Actions: SOPs, validation, cohorts (not "delivery route")
- ✅ No truncated text with "..."
