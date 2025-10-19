"""
Full Hypothesis Inspector - View Complete DeepSeek Outputs

Generates a detailed markdown report with ALL LLM responses and agent outputs
for a hypothesis generation run. Like having a UI to inspect every step.

Usage:
    python inspect_hypothesis.py --live          # Run new hypothesis with full output
    python inspect_hypothesis.py --id <ID>       # Inspect existing from MongoDB
    python inspect_hypothesis.py --file <path>   # Inspect from JSON result file
"""

import asyncio
import argparse
import json
from datetime import datetime
from pathlib import Path

from medical_discovery.services.orchestrator import HypothesisOrchestrator
from medical_discovery.api.schemas.hypothesis import (
    HypothesisRequest, 
    MedicalDomain,
    HypothesisConstraints
)


async def inspect_live_run():
    """
    Run a new hypothesis generation and capture EVERYTHING.
    Returns full report with all DeepSeek outputs.
    """
    print("="*80)
    print("🔬 LIVE HYPOTHESIS INSPECTION - Full Output Capture")
    print("="*80)
    
    # Create test hypothesis
    hypothesis_id = f"inspect_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    request = HypothesisRequest(
        goal="Develop a novel CAR-T therapy for glioblastoma using BBB-penetrating nanoparticles",
        domain=MedicalDomain.ONCOLOGY,
        constraints=HypothesisConstraints(
            focus=["Must cross blood-brain barrier", "Target tumor microenvironment", 
                   "immunotherapy", "nanomedicine"]
        )
    )
    
    print(f"\n📋 Hypothesis ID: {hypothesis_id}")
    print(f"🎯 Goal: {request.goal}")
    print(f"🧬 Domain: {request.domain.value}\n")
    
    # Initialize orchestrator
    orchestrator = HypothesisOrchestrator()
    
    # Run generation
    print("⏳ Running 7-agent pipeline (this takes ~6 minutes)...\n")
    result = await orchestrator.generate_hypothesis(hypothesis_id, request)
    
    # Generate full report
    report_path = generate_markdown_report(result, hypothesis_id)
    
    print(f"\n✅ INSPECTION COMPLETE!")
    print(f"📄 Full report: {report_path}")
    print(f"📊 Total stages: 7")
    print(f"📝 Evidence collected: {len(result.get('evidence_packs', []))}")
    
    # Safe access to divergent variants
    hypothesis_doc = result.get('hypothesis_doc', {})
    variants = hypothesis_doc.get('divergent_variants', []) if hypothesis_doc else []
    print(f"🔀 Divergent variants: {len(variants)}")
    
    return report_path


def generate_markdown_report(result: dict, hypothesis_id: str) -> Path:
    """
    Generate comprehensive markdown report with ALL outputs.
    
    Includes:
    - Executive summary
    - Stage-by-stage DeepSeek outputs
    - Evidence details
    - Reasoning trace
    - Full narrative
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = Path(f"reports/inspection_{hypothesis_id}_{timestamp}.md")
    report_path.parent.mkdir(exist_ok=True)
    
    hypothesis_doc = result.get("hypothesis_doc", {})
    reasoning_steps = result.get("reasoning_steps", [])
    evidence_packs = result.get("evidence_packs", [])
    reasoning_trace = result.get("reasoning_trace", [])
    narrative = result.get("narrative", {})
    executive_summary = result.get("executive_summary", {})
    
    # Extract title/domain from executive_summary (narrative_generator passes them)
    title = executive_summary.get("title") or hypothesis_doc.get("title", "N/A")
    domain = executive_summary.get("domain") or hypothesis_doc.get("domain", "N/A")
    
    with open(report_path, "w", encoding="utf-8") as f:
        # Header
        f.write(f"# 🔬 Hypothesis Inspection Report\n\n")
        f.write(f"**Hypothesis ID**: `{hypothesis_id}`  \n")
        f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n")
        f.write(f"**Domain**: {domain}  \n")
        f.write(f"**Title**: {title}  \n\n")
        
        f.write("---\n\n")
        
        # Table of Contents
        f.write("## 📑 Table of Contents\n\n")
        f.write("1. [Executive Summary](#executive-summary)\n")
        f.write("2. [Stage 1: Visioner Agent](#stage-1-visioner-agent)\n")
        f.write("3. [Stage 2: Concept Learner](#stage-2-concept-learner)\n")
        f.write("4. [Stage 3: Evidence Miner](#stage-3-evidence-miner)\n")
        f.write("5. [Stage 4: Cross-Domain Mapper](#stage-4-cross-domain-mapper)\n")
        f.write("6. [Stage 5: Synthesizer](#stage-5-synthesizer)\n")
        f.write("7. [Stage 6: Simulation Agent](#stage-6-simulation-agent)\n")
        f.write("8. [Stage 7: Ethics Validator](#stage-7-ethics-validator)\n")
        f.write("9. [Reasoning Trace](#reasoning-trace)\n")
        f.write("10. [Full Narrative](#full-narrative)\n\n")
        
        f.write("---\n\n")
        
        # Executive Summary
        f.write("## 🎯 Executive Summary\n\n")
        if executive_summary:
            f.write(f"**Elevator Pitch**:\n{executive_summary.get('elevator_pitch', 'N/A')}\n\n")
            f.write(f"**Key Innovation**:\n{executive_summary.get('key_innovation', 'N/A')}\n\n")
            f.write(f"**Evidence Strength**: {executive_summary.get('evidence_strength', 'N/A')}\n\n")
            f.write(f"**Feasibility Verdict**: {executive_summary.get('feasibility_verdict', 'N/A')}\n\n")
        
        f.write("---\n\n")
        
        # Stage 1: Visioner
        f.write("## 🔭 Stage 1: Visioner Agent\n\n")
        f.write("**Purpose**: Generate 4 research directions\n\n")
        
        # Try multiple sources: hypothesis_doc, reasoning_trace, concept_map
        directions = hypothesis_doc.get("research_directions", [])
        if not directions and reasoning_trace:
            visioner_step = next((s for s in reasoning_trace if "visioner" in s.get("stage", "").lower()), None)
            if visioner_step and visioner_step.get("output"):
                output = visioner_step["output"]
                if isinstance(output, dict):
                    directions = output.get("directions", output.get("research_directions", []))
        
        if directions:
            f.write(f"**Generated {len(directions)} directions**:\n\n")
            for i, direction in enumerate(directions, 1):
                if isinstance(direction, dict):
                    f.write(f"### Direction {i}: {direction.get('title', 'N/A')}\n\n")
                    f.write(f"**Rationale**: {direction.get('rationale', 'N/A')}\n\n")
                    mechanisms = direction.get("key_mechanisms", [])
                    if mechanisms:
                        f.write("**Key Mechanisms**:\n")
                        for mechanism in mechanisms:
                            f.write(f"- {mechanism}\n")
                        f.write("\n")
                    f.write(f"**Novelty Score**: {direction.get('novelty', 0):.2f}  \n")
                    f.write(f"**Feasibility Score**: {direction.get('feasibility', 0):.2f}\n\n")
                else:
                    f.write(f"- {direction}\n\n")
        else:
            f.write("*No directions data available in output*\n\n")
        
        f.write("---\n\n")
        
        # Stage 2: Concept Learner
        f.write("## 🧠 Stage 2: Concept Learner\n\n")
        f.write("**Purpose**: Build biomedical concept map\n\n")
        
        concept_map = result.get("concept_map", {})
        concepts = concept_map.get("concepts", [])
        pathways = concept_map.get("pathways", [])
        
        if concepts:
            f.write(f"**Identified {len(concepts)} concepts**:\n\n")
            for concept in concepts[:10]:  # First 10
                f.write(f"### {concept.get('term', 'N/A')}\n\n")
                f.write(f"**Definition**: {concept.get('definition', 'N/A')}\n\n")
                f.write(f"**Biological Role**: {concept.get('biological_role', 'N/A')}\n\n")
                genes = concept.get("genes", [])
                if genes:
                    f.write(f"**Genes**: {', '.join(genes[:5])}\n\n")
        
        if pathways:
            f.write(f"\n**Key Pathways ({len(pathways)})**:\n\n")
            for pathway in pathways:
                f.write(f"- {pathway}\n")
            f.write("\n")
        
        f.write("---\n\n")
        
        # Stage 3: Evidence Miner
        f.write("## 📚 Stage 3: Evidence Miner\n\n")
        f.write("**Purpose**: Gather multi-source evidence\n\n")
        
        f.write(f"**Total Evidence**: {len(evidence_packs)} items\n\n")
        
        # Evidence breakdown by source
        sources = {}
        for ev in evidence_packs:
            source = ev.get("source", "unknown")
            sources[source] = sources.get(source, 0) + 1
        
        f.write("**Sources**:\n\n")
        for source, count in sources.items():
            f.write(f"- {source}: {count} items\n")
        f.write("\n")
        
        # Top 5 evidence items
        f.write("**Top 5 Evidence Items**:\n\n")
        for i, ev in enumerate(evidence_packs[:5], 1):
            f.write(f"### {i}. {ev.get('title', 'N/A')}\n\n")
            f.write(f"**Source**: {ev.get('source', 'N/A')}  \n")
            f.write(f"**Confidence**: {ev.get('confidence_score', 0):.2f}  \n")
            f.write(f"**Tier**: {ev.get('evidence_tier', 'N/A')}  \n")
            
            # Epistemic metadata
            epistemic = ev.get("epistemic_metadata", {})
            if epistemic:
                f.write(f"**Study Type**: {epistemic.get('study_type', 'N/A')}  \n")
                f.write(f"**Epistemic Weight**: {epistemic.get('weight', 0):.2f}  \n")
            
            # Abstract (first 300 chars)
            abstract = ev.get("abstract", "")
            if abstract:
                f.write(f"\n**Abstract**: {abstract[:300]}...\n\n")
            f.write("\n")
        
        f.write("---\n\n")
        
        # Stage 4: Cross-Domain Mapper
        f.write("## 🌐 Stage 4: Cross-Domain Mapper\n\n")
        f.write("**Purpose**: Find analogies from other fields\n\n")
        
        # Try multiple sources
        transfers = hypothesis_doc.get("cross_domain_transfers", [])
        if not transfers:
            transfers = result.get("cross_domain_transfers", [])
        if not transfers and reasoning_trace:
            cross_step = next((s for s in reasoning_trace if "cross" in s.get("stage", "").lower()), None)
            if cross_step and cross_step.get("output"):
                output = cross_step["output"]
                if isinstance(output, dict):
                    transfers = output.get("transfers", [])
                elif isinstance(output, list):
                    transfers = output
        
        if transfers:
            f.write(f"**Found {len(transfers)} transfers**:\n\n")
            for i, transfer in enumerate(transfers, 1):
                if isinstance(transfer, dict):
                    f.write(f"### Transfer {i}: {transfer.get('source_domain', 'N/A')} → Medicine\n\n")
                    f.write(f"**Concept**: {transfer.get('concept', 'N/A')}\n\n")
                    f.write(f"**Application**: {transfer.get('application', 'N/A')}\n\n")
                    f.write(f"**Relevance**: {transfer.get('relevance', 0):.2f}  \n")
                    f.write(f"**Testability**: {transfer.get('testability', 0):.2f}\n\n")
                else:
                    f.write(f"- {transfer}\n\n")
        else:
            f.write("*No cross-domain transfers data available*\n\n")
        
        f.write("---\n\n")
        
        # Stage 5: Synthesizer
        f.write("## 🔬 Stage 5: Synthesizer\n\n")
        f.write("**Purpose**: Synthesize comprehensive hypothesis\n\n")
        
        # Use title/domain extracted earlier
        f.write(f"**Title**: {title}\n\n")
        
        # Try multiple sources for abstract/mechanism
        abstract = hypothesis_doc.get("abstract") or hypothesis_doc.get("mechanism_of_action", "N/A")
        f.write(f"**Abstract**:\n{abstract}\n\n")
        
        # Divergent Variants (Nobel 3.0 LITE)
        divergent_variants = hypothesis_doc.get("divergent_variants", [])
        if divergent_variants:
            f.write(f"\n### 🔀 Divergent Variants ({len(divergent_variants)})\n\n")
            for i, variant in enumerate(divergent_variants, 1):
                f.write(f"#### Variant {i}: {variant.get('type', 'N/A')}\n\n")
                f.write(f"**Claim**: {variant.get('claim', 'N/A')}\n\n")
                f.write(f"**Novelty**: {variant.get('novelty', 'N/A')}\n\n")
                f.write(f"**Testability**: {variant.get('testability', 'N/A')}\n\n")
                f.write(f"**Plausibility**: {variant.get('plausibility', 0):.2f}\n\n")
        
        f.write("---\n\n")
        
        # Stage 6: Simulation
        f.write("## 🧪 Stage 6: Simulation Agent\n\n")
        f.write("**Purpose**: Assess feasibility\n\n")
        
        simulation = result.get("simulation_scorecard", {})
        if simulation:
            f.write(f"**Overall Feasibility**: {simulation.get('overall_feasibility', 'N/A')}\n\n")
            f.write(f"**Feasibility Score**: {simulation.get('feasibility_score', 0):.2f}\n\n")
            f.write(f"**Technical Feasibility**: {simulation.get('technical_feasibility', 0):.2f}\n")
            f.write(f"**Clinical Translatability**: {simulation.get('clinical_translatability', 0):.2f}\n")
            f.write(f"**Safety Profile**: {simulation.get('safety_profile', 0):.2f}\n")
            f.write(f"**Regulatory Path**: {simulation.get('regulatory_path_ready', 0):.2f}\n\n")
        
        f.write("---\n\n")
        
        # Stage 7: Ethics
        f.write("## ⚖️ Stage 7: Ethics Validator\n\n")
        f.write("**Purpose**: Validate ethics & safety\n\n")
        
        ethics = result.get("ethics_report", {})
        if ethics:
            f.write(f"**Verdict**: {ethics.get('verdict', 'N/A')}\n\n")
            f.write(f"**Verdict Reasoning**: {ethics.get('verdict_reasoning', 'N/A')}\n\n")
            
            # Fragile Assumptions (Nobel 3.0 LITE)
            fragile = ethics.get("fragile_assumptions", [])
            if fragile:
                f.write(f"\n### ⚠️ Fragile Assumptions ({len(fragile)})\n\n")
                for i, assumption in enumerate(fragile, 1):
                    f.write(f"**{i}. {assumption.get('assumption', 'N/A')}**\n\n")
                    f.write(f"Impact: {assumption.get('impact', 'N/A')}\n\n")
                    f.write(f"Mitigation: {assumption.get('mitigation', 'N/A')}\n\n")
            
            # Confounders
            confounders = ethics.get("potential_confounders", [])
            if confounders:
                f.write(f"\n### 🔍 Potential Confounders ({len(confounders)})\n\n")
                for confounder in confounders:
                    f.write(f"- {confounder}\n")
                f.write("\n")
        
        f.write("---\n\n")
        
        # Reasoning Trace
        f.write("## 🧵 Reasoning Trace\n\n")
        f.write("**Purpose**: Audit trail of all decisions\n\n")
        
        if reasoning_trace:
            f.write(f"**Total Stages**: {len(reasoning_trace)}\n\n")
            for trace in reasoning_trace:
                f.write(f"### {trace.get('stage', 'N/A').title()}\n\n")
                f.write(f"**Agent**: {trace.get('agent', 'N/A')}  \n")
                f.write(f"**Duration**: {trace.get('duration_ms', 0):,} ms  \n")
                f.write(f"**Input**: {trace.get('input_summary', 'N/A')}  \n")
                f.write(f"**Output**: {trace.get('output_summary', 'N/A')}  \n\n")
                
                decisions = trace.get("key_decisions", [])
                if decisions:
                    f.write("**Key Decisions**:\n")
                    for decision in decisions:
                        f.write(f"- {decision}\n")
                    f.write("\n")
        
        f.write("---\n\n")
        
        # Full Narrative
        f.write("## 📄 Full Narrative (JSON)\n\n")
        f.write("```json\n")
        f.write(json.dumps(narrative, indent=2, ensure_ascii=False))
        f.write("\n```\n\n")
        
        # Executive Summary Full
        f.write("## 📊 Executive Summary (Full)\n\n")
        f.write("```json\n")
        f.write(json.dumps(executive_summary, indent=2, ensure_ascii=False))
        f.write("\n```\n\n")
    
    return report_path


def inspect_from_file(file_path: str):
    """Load hypothesis result from JSON file and generate report."""
    with open(file_path, "r", encoding="utf-8") as f:
        result = json.load(f)
    
    hypothesis_id = result.get("hypothesis_id", "unknown")
    report_path = generate_markdown_report(result, hypothesis_id)
    
    print(f"✅ Report generated: {report_path}")
    return report_path


async def main():
    parser = argparse.ArgumentParser(
        description="Inspect hypothesis generation with full DeepSeek outputs"
    )
    parser.add_argument(
        "--live",
        action="store_true",
        help="Run new hypothesis generation with full capture"
    )
    parser.add_argument(
        "--file",
        type=str,
        help="Path to JSON result file to inspect"
    )
    parser.add_argument(
        "--open",
        action="store_true",
        help="Auto-open report in browser/editor after generation"
    )
    
    args = parser.parse_args()
    
    if args.live:
        report_path = await inspect_live_run()
    elif args.file:
        report_path = inspect_from_file(args.file)
    else:
        print("❌ Error: Must specify --live or --file <path>")
        parser.print_help()
        return
    
    # Auto-open if requested
    if args.open:
        import webbrowser
        webbrowser.open(f"file://{report_path.absolute()}")


if __name__ == "__main__":
    asyncio.run(main())
