NOBEL 3.0 LITE — Project Summary

Overview
--------
NOBEL 3.0 LITE is a production-focused instantiation of the Nobel architecture for AI-assisted hypothesis generation and evaluation in biomedical research. It orchestrates seven specialized agents to transform a research goal into a transparent, evidence-grounded hypothesis with actionable validation steps and risk assessment.

Key Capabilities
----------------
- 7-agent pipeline (Visioner, Concept Learner, Evidence Miner, Cross-Domain Mapper, Synthesizer, Simulation, Ethics)
- Epistemic scoring v2 (study-type-aware weighting)
- Divergent idea generation with testability and novelty scoring
- Adversarial review with fragile assumption detection
- Reasoning trace: full timeline and agent outputs (suitable for UI tracing)
- Inspector tool producing full Markdown reports for auditing

Recent Surgical Fixes
---------------------
1. Single-source feasibility score and unified label (Simulation Agent).
2. Narrative template sanitization and explicit metadata export (Narrative Generator).
3. Inspector robustness: title/domain extraction, safe fallbacks, and improved section rendering.
4. Epistemic extractor: stronger regex patterns, venue mapping, added `in_vivo` type, unknown weight lowered to 0.25.
5. Evidence relevance scoring: domain boosts and TfR de-boost for non-brain contexts.
6. Defensive connector parsing (ChEMBL None handling).

How to run
----------
- Install dependencies: `pip install -r requirements.txt`
- Run full inspector: `python inspect_hypothesis.py --live`
- Run unit tests: `pytest -q`

Design Decisions & Rationale
----------------------------
- Explicit single-source truth for composite feasibility prevents inconsistent labels across summary and simulation logs.
- Conservative handling of unknown study types preserves safety but pushes for higher coverage via regex and venue signals.
- Domain-aware relevance improves external validity by preferring context-specific evidence and de-emphasizing generic vascular TfR studies.

Short-Term Roadmap
------------------
- Implement synthesizer scientific upgrades: SynNotch AND gates, TRUCK/armored CAR-T patterns, FUS+microbubble delivery templates, exosome-RVG tropism.
- Add API endpoints for trace visualization and an `evaluate_nobel_lite.py` benchmarking script.
- CI: add smoke tests for inspector and unit tests for epistemic extractor/evidence scorer.

Contact
-------
Repository owner: panosbee (https://github.com/panosbee)

