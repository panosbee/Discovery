"""
Realistic Research Scenarios Test
Tests the Medical Discovery & Hypothesis Engine with real-world research questions
"""

import asyncio
import httpx
from datetime import datetime
from typing import Dict, Any

# Base URL
BASE_URL = "http://localhost:8000"

# Color codes for output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_header(text: str):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*80}{Colors.END}\n")

def print_section(text: str):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'─'*80}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'─'*80}{Colors.END}\n")

def print_success(text: str):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_info(text: str):
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

def print_warning(text: str):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_error(text: str):
    print(f"{Colors.RED}✗ {text}{Colors.END}")


# Research Scenarios (as a real researcher would ask)
RESEARCH_SCENARIOS = [
    {
        "name": "Alzheimer's Breakthrough (Neurology)",
        "goal": "Identify novel biomarkers for early detection of Alzheimer's disease using liquid biopsy and machine learning",
        "domain": "neurology",
        "constraints": {
            "focus": [
                "blood biomarkers",
                "proteomics",
                "exosomes",
                "machine learning diagnostics",
                "early stage detection"
            ],
            "avoid": [
                "invasive procedures",
                "CSF sampling",
                "expensive imaging"
            ],
            "timeline": "3-5 years"
        },
        "expected_evidence_sources": ["PubMed", "Crossref", "UniProt", "ClinicalTrials.gov", "arXiv"],
        "expected_concepts": ["amyloid", "tau", "neurodegeneration", "biomarkers", "proteomics"]
    },
    {
        "name": "Cancer Immunotherapy (Oncology)",
        "goal": "Develop personalized combination immunotherapy for triple-negative breast cancer using tumor microenvironment profiling",
        "domain": "oncology",
        "constraints": {
            "focus": [
                "checkpoint inhibitors",
                "CAR-T cells",
                "tumor microenvironment",
                "immune infiltration",
                "personalized medicine"
            ],
            "avoid": [
                "traditional chemotherapy alone",
                "hormone therapy"
            ],
            "timeline": "5-7 years"
        },
        "expected_evidence_sources": ["PubMed", "ClinicalTrials.gov", "ChEMBL", "Crossref", "UniProt"],
        "expected_concepts": ["immunotherapy", "PD-1", "PD-L1", "T cells", "tumor"]
    },
    {
        "name": "Cardiovascular Prevention (Cardiology)",
        "goal": "Create AI-powered risk prediction model for sudden cardiac death in young athletes using wearable sensor data",
        "domain": "cardiology",
        "constraints": {
            "focus": [
                "wearable sensors",
                "ECG monitoring",
                "machine learning",
                "arrhythmia detection",
                "genetic markers"
            ],
            "avoid": [
                "invasive monitoring",
                "implantable devices"
            ],
            "timeline": "2-4 years"
        },
        "expected_evidence_sources": ["PubMed", "ClinicalTrials.gov", "arXiv", "Kaggle", "Zenodo"],
        "expected_concepts": ["cardiac", "arrhythmia", "ECG", "prediction", "wearables"]
    }
]


async def test_health_check():
    """Test if the system is ready"""
    print_section("🏥 Health Check")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.get(f"{BASE_URL}/health")
            if response.status_code == 200:
                data = response.json()
                print_success(f"Server is {data['status']}")
                print_info(f"Version: {data.get('version', 'N/A')}")
                print_info(f"MongoDB Connected: {data.get('mongodb_connected', False)}")
                
                # Check intelligence modules
                if 'intelligence_modules' in data:
                    print_success("Intelligence modules detected:")
                    for module in data['intelligence_modules']:
                        print(f"    • {module}")
                
                return True
            else:
                print_error(f"Health check failed with status {response.status_code}")
                return False
        except Exception as e:
            print_error(f"Health check failed: {str(e)}")
            return False


async def create_hypothesis(scenario: Dict[str, Any]) -> str:
    """Create hypothesis for a research scenario"""
    print_section(f"🔬 Creating Hypothesis: {scenario['name']}")
    
    print_info(f"Research Goal: {scenario['goal']}")
    print_info(f"Domain: {scenario['domain']}")
    print_info(f"Focus Areas: {', '.join(scenario['constraints']['focus'][:3])}...")
    
    request_body = {
        "goal": scenario["goal"],
        "domain": scenario["domain"],
        "constraints": scenario["constraints"]
    }
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            response = await client.post(
                f"{BASE_URL}/v1/hypotheses",
                json=request_body
            )
            
            if response.status_code == 202:
                result = response.json()
                hypothesis_id = result.get("id") or result.get("hypothesis_id")
                print_success(f"Hypothesis created: {hypothesis_id}")
                print_info(f"Status: {result.get('status', 'unknown')}")
                print_info(f"Message: {result.get('message', 'Processing started')}")
                return hypothesis_id
            else:
                print_error(f"Failed to create hypothesis: {response.status_code}")
                print_error(response.text)
                return None
                
        except Exception as e:
            print_error(f"Error creating hypothesis: {str(e)}")
            return None


async def monitor_hypothesis_progress(hypothesis_id: str, max_wait: int = 600) -> Dict[str, Any]:
    """Monitor hypothesis generation progress"""
    print_section(f"⏳ Monitoring Progress: {hypothesis_id}")
    
    start_time = datetime.now()
    last_status = None
    check_count = 0
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        while True:
            try:
                response = await client.get(f"{BASE_URL}/v1/hypotheses/{hypothesis_id}")
                
                if response.status_code == 200:
                    data = response.json()
                    current_status = data.get("status", "unknown")
                    
                    # Print status updates
                    if current_status != last_status:
                        elapsed = (datetime.now() - start_time).seconds
                        print_info(f"[{elapsed}s] Status: {current_status}")
                        last_status = current_status
                    
                    # Check provenance for step updates
                    if data.get("provenance"):
                        latest_step = data["provenance"][-1]
                        agent = latest_step.get("agent", "Unknown")
                        action = latest_step.get("action", "")
                        print(f"    └─ Latest: {agent} - {action[:60]}...")
                    
                    # Check if completed or failed
                    if current_status == "completed":
                        elapsed = (datetime.now() - start_time).seconds
                        print_success(f"Hypothesis completed in {elapsed} seconds!")
                        return data
                    
                    elif current_status == "failed":
                        print_error("Hypothesis generation failed")
                        print_error(f"Error: {data.get('error', 'Unknown error')}")
                        return data
                    
                    # Check timeout
                    elapsed = (datetime.now() - start_time).seconds
                    if elapsed > max_wait:
                        print_warning(f"Timeout reached ({max_wait}s)")
                        return data
                    
                    # Wait before next check
                    check_count += 1
                    wait_time = min(5 + (check_count // 5), 15)  # Progressive wait: 5s -> 15s
                    await asyncio.sleep(wait_time)
                
                else:
                    print_error(f"Failed to get hypothesis: {response.status_code}")
                    return None
                    
            except Exception as e:
                print_error(f"Error monitoring hypothesis: {str(e)}")
                await asyncio.sleep(5)


def analyze_evidence_quality(hypothesis: Dict[str, Any], scenario: Dict[str, Any]):
    """Analyze the quality of gathered evidence"""
    print_section("📊 Evidence Quality Analysis")
    
    evidence_packs = hypothesis.get("evidence_packs", [])
    
    if not evidence_packs:
        print_warning("No evidence packs found")
        return
    
    print_info(f"Total Evidence Packs: {len(evidence_packs)}")
    
    # Analyze by source
    by_source = {}
    for evidence in evidence_packs:
        source = evidence.get("source", "Unknown")
        by_source[source] = by_source.get(source, 0) + 1
    
    print("\n📚 Evidence by Source:")
    for source, count in sorted(by_source.items(), key=lambda x: x[1], reverse=True):
        expected = "✓" if source in scenario.get("expected_evidence_sources", []) else ""
        print(f"    • {source}: {count} {expected}")
    
    # Analyze by evidence tier (if available)
    if any("evidence_tier" in e for e in evidence_packs):
        print("\n🏆 Evidence Quality Tiers:")
        by_tier = {}
        for evidence in evidence_packs:
            tier = evidence.get("evidence_tier", "UNKNOWN")
            by_tier[tier] = by_tier.get(tier, 0) + 1
        
        tier_order = ["TIER_1_EXCEPTIONAL", "TIER_2_HIGH", "TIER_3_MODERATE", "TIER_4_LOW", "TIER_5_MARGINAL", "UNKNOWN"]
        for tier in tier_order:
            if tier in by_tier:
                count = by_tier[tier]
                percentage = (count / len(evidence_packs)) * 100
                bar = "█" * int(percentage / 2)
                print(f"    {tier:20s}: {count:3d} ({percentage:5.1f}%) {bar}")
    
    # Analyze confidence scores (if available)
    if any("confidence_score" in e for e in evidence_packs):
        confidence_scores = [e.get("confidence_score", 0) for e in evidence_packs if "confidence_score" in e]
        if confidence_scores:
            avg_confidence = sum(confidence_scores) / len(confidence_scores)
            max_confidence = max(confidence_scores)
            min_confidence = min(confidence_scores)
            
            print(f"\n📈 Confidence Scores:")
            print(f"    • Average: {avg_confidence:.3f}")
            print(f"    • Maximum: {max_confidence:.3f}")
            print(f"    • Minimum: {min_confidence:.3f}")
            
            # Show top 3 evidence by confidence
            top_evidence = sorted(evidence_packs, key=lambda x: x.get("confidence_score", 0), reverse=True)[:3]
            print(f"\n🌟 Top 3 Evidence (by confidence):")
            for i, evidence in enumerate(top_evidence, 1):
                title = evidence.get("title", "No title")[:60]
                confidence = evidence.get("confidence_score", 0)
                source = evidence.get("source", "Unknown")
                print(f"    {i}. [{confidence:.3f}] {source}: {title}...")
    
    # Check for expected concepts
    print(f"\n🔍 Concept Coverage:")
    hypothesis_text = str(hypothesis).lower()
    for concept in scenario.get("expected_concepts", []):
        found = concept.lower() in hypothesis_text
        status = "✓" if found else "✗"
        print(f"    {status} {concept}")


def analyze_hypothesis_document(hypothesis: Dict[str, Any]):
    """Analyze the generated hypothesis document"""
    print_section("📝 Hypothesis Document Analysis")
    
    doc = hypothesis.get("hypothesis_document", {})
    
    if not doc:
        print_warning("No hypothesis document found")
        return
    
    print(f"{Colors.BOLD}Title:{Colors.END}")
    print(f"    {doc.get('title', 'N/A')}\n")
    
    print(f"{Colors.BOLD}Abstract:{Colors.END}")
    abstract = doc.get("abstract", "N/A")
    print(f"    {abstract[:300]}...\n")
    
    print(f"{Colors.BOLD}Novelty Score:{Colors.END} {doc.get('novelty_score', 'N/A')}")
    
    if doc.get("methodology"):
        print(f"\n{Colors.BOLD}Methodology Approach:{Colors.END}")
        methodology = doc.get("methodology", "")[:200]
        print(f"    {methodology}...")


def analyze_feasibility_and_ethics(hypothesis: Dict[str, Any]):
    """Analyze feasibility and ethics assessments"""
    print_section("⚖️ Feasibility & Ethics Analysis")
    
    # Feasibility
    simulation = hypothesis.get("simulation_scorecard", {})
    if simulation:
        feasibility = simulation.get("overall_feasibility", "UNKNOWN")
        color = Colors.GREEN if feasibility == "GREEN" else Colors.YELLOW if feasibility == "AMBER" else Colors.RED
        print(f"{Colors.BOLD}Overall Feasibility:{Colors.END} {color}{feasibility}{Colors.END}")
        
        scores = simulation.get("scores", {})
        if scores:
            print(f"\n{Colors.BOLD}Dimension Scores:{Colors.END}")
            for dimension, score in scores.items():
                bar = "█" * int(score * 10)
                print(f"    • {dimension:30s}: {score:.2f} {bar}")
    
    # Ethics
    ethics = hypothesis.get("ethics_report", {})
    if ethics:
        verdict = ethics.get("verdict", "UNKNOWN")
        color = Colors.GREEN if verdict == "GREEN" else Colors.YELLOW if verdict == "AMBER" else Colors.RED
        print(f"\n{Colors.BOLD}Ethics Verdict:{Colors.END} {color}{verdict}{Colors.END}")
        
        considerations = ethics.get("considerations", [])
        if considerations:
            print(f"\n{Colors.BOLD}Key Ethical Considerations:{Colors.END}")
            for consideration in considerations[:5]:
                print(f"    • {consideration}")


def analyze_cross_domain_innovation(hypothesis: Dict[str, Any]):
    """Analyze cross-domain transfers"""
    print_section("🌐 Cross-Domain Innovation")
    
    transfers = hypothesis.get("cross_domain_transfers", [])
    
    if not transfers:
        print_warning("No cross-domain transfers found")
        return
    
    print_info(f"Found {len(transfers)} cross-domain transfers")
    
    for i, transfer in enumerate(transfers[:3], 1):  # Show top 3
        print(f"\n{Colors.BOLD}{i}. {transfer.get('source_domain', 'Unknown')} → {hypothesis.get('domain', 'Unknown')}{Colors.END}")
        print(f"    Concept: {transfer.get('concept_transferred', 'N/A')}")
        print(f"    Analogy: {transfer.get('analogy', 'N/A')[:100]}...")
        print(f"    Relevance: {transfer.get('relevance_score', 'N/A')}")


def analyze_nobel_reasoning(hypothesis: Dict[str, Any]):
    """Analyze Nobel-Level transparent reasoning (Phase 1)"""
    print_section("🧠 Nobel-Level Transparent Reasoning")
    
    reasoning_steps = hypothesis.get("reasoning_steps", [])
    reasoning_narrative = hypothesis.get("reasoning_narrative", "")
    
    if not reasoning_steps:
        print_warning("No reasoning steps found (Nobel Phase 1 not active)")
        return
    
    print_success(f"Found {len(reasoning_steps)} reasoning steps showing HOW the system made decisions")
    
    # Show key reasoning steps
    for i, step in enumerate(reasoning_steps, 1):
        agent = step.get("agent", "Unknown")
        action = step.get("action", "Unknown")
        question = step.get("question_asked", "")
        key_insight = step.get("key_insight", "")
        confidence = step.get("confidence", 0.0)
        
        # Confidence bar
        confidence_bar = "█" * int(confidence * 10)
        confidence_color = Colors.GREEN if confidence >= 0.8 else Colors.YELLOW if confidence >= 0.6 else Colors.RED
        
        print(f"\n{Colors.BOLD}Step {i}: {agent} - {action}{Colors.END}")
        if question:
            print(f"    ❓ Question: {question}")
        if key_insight:
            print(f"    💡 Key Insight: {key_insight[:150]}{'...' if len(key_insight) > 150 else ''}")
        print(f"    📊 Confidence: {confidence_color}{confidence:.2f}{Colors.END} {confidence_bar}")
    
    # Show reasoning narrative summary
    if reasoning_narrative:
        print(f"\n{Colors.BOLD}📖 Reasoning Narrative Summary:{Colors.END}")
        # Show first 500 chars of narrative
        narrative_preview = reasoning_narrative[:500]
        print(f"{Colors.CYAN}{narrative_preview}...{Colors.END}")
        print_info(f"Full narrative: {len(reasoning_narrative)} characters")
    
    print(f"\n{Colors.GREEN}✓ Transparent reasoning enables researchers to understand WHY and HOW decisions were made{Colors.END}")


async def test_scenario(scenario: Dict[str, Any]):
    """Test a complete research scenario"""
    print_header(f"🧪 RESEARCH SCENARIO: {scenario['name']}")
    
    # Create hypothesis
    hypothesis_id = await create_hypothesis(scenario)
    if not hypothesis_id:
        print_error("Failed to create hypothesis")
        return None
    
    # Monitor progress
    hypothesis = await monitor_hypothesis_progress(hypothesis_id, max_wait=600)
    if not hypothesis:
        print_error("Failed to get hypothesis results")
        return None
    
    # Analyze results
    if hypothesis.get("status") == "completed":
        analyze_evidence_quality(hypothesis, scenario)
        analyze_hypothesis_document(hypothesis)
        analyze_cross_domain_innovation(hypothesis)
        analyze_feasibility_and_ethics(hypothesis)
        analyze_nobel_reasoning(hypothesis)  # Nobel-Level Transparency!
        
        print_section("✅ Scenario Test Complete")
        return hypothesis
    else:
        print_warning(f"Hypothesis status: {hypothesis.get('status')}")
        return hypothesis


async def main():
    """Run all research scenarios"""
    print_header("🧬 MEDICAL DISCOVERY ENGINE - REALISTIC RESEARCH TEST")
    print(f"{Colors.BOLD}Testing as a real researcher with breakthrough questions{Colors.END}\n")
    
    # Health check
    if not await test_health_check():
        print_error("System not ready. Exiting.")
        return
    
    print_info(f"\n{Colors.BOLD}Running {len(RESEARCH_SCENARIOS)} realistic research scenarios...{Colors.END}\n")
    
    # Test each scenario
    results = []
    for i, scenario in enumerate(RESEARCH_SCENARIOS, 1):
        print(f"\n{Colors.YELLOW}{'═'*80}{Colors.END}")
        print(f"{Colors.YELLOW}{Colors.BOLD}SCENARIO {i}/{len(RESEARCH_SCENARIOS)}{Colors.END}")
        print(f"{Colors.YELLOW}{'═'*80}{Colors.END}\n")
        
        result = await test_scenario(scenario)
        results.append({
            "scenario": scenario["name"],
            "hypothesis": result
        })
        
        # Wait between scenarios
        if i < len(RESEARCH_SCENARIOS):
            print_info(f"\nWaiting 30 seconds before next scenario...")
            await asyncio.sleep(30)
    
    # Final summary
    print_header("📊 FINAL SUMMARY")
    
    completed = sum(1 for r in results if r["hypothesis"] and r["hypothesis"].get("status") == "completed")
    print_info(f"Scenarios Completed: {completed}/{len(RESEARCH_SCENARIOS)}")
    
    for i, result in enumerate(results, 1):
        status = result["hypothesis"].get("status") if result["hypothesis"] else "failed"
        color = Colors.GREEN if status == "completed" else Colors.RED
        print(f"    {i}. {result['scenario']:50s} [{color}{status}{Colors.END}]")
    
    # Nobel-Level Transparency Statistics
    print_section("🧠 Nobel-Level Transparency Statistics")
    
    total_reasoning_steps = 0
    total_narrative_length = 0
    avg_confidence_scores = []
    
    for result in results:
        if result["hypothesis"] and result["hypothesis"].get("status") == "completed":
            reasoning_steps = result["hypothesis"].get("reasoning_steps", [])
            reasoning_narrative = result["hypothesis"].get("reasoning_narrative", "")
            
            total_reasoning_steps += len(reasoning_steps)
            total_narrative_length += len(reasoning_narrative)
            
            # Calculate average confidence per hypothesis
            if reasoning_steps:
                confidences = [step.get("confidence", 0.0) for step in reasoning_steps]
                avg_conf = sum(confidences) / len(confidences)
                avg_confidence_scores.append(avg_conf)
    
    if total_reasoning_steps > 0:
        print_success(f"Total Reasoning Steps Captured: {total_reasoning_steps}")
        print_success(f"Total Narrative Content: {total_narrative_length:,} characters")
        
        if avg_confidence_scores:
            overall_avg_confidence = sum(avg_confidence_scores) / len(avg_confidence_scores)
            confidence_bar = "█" * int(overall_avg_confidence * 10)
            confidence_color = Colors.GREEN if overall_avg_confidence >= 0.8 else Colors.YELLOW
            print_success(f"Average Decision Confidence: {confidence_color}{overall_avg_confidence:.2f}{Colors.END} {confidence_bar}")
        
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ Nobel-Level Transparency Active:{Colors.END}")
        print(f"  Researchers can now see HOW and WHY each decision was made!")
        print(f"  Every hypothesis includes step-by-step reasoning with:")
        print(f"    • Questions addressed at each step")
        print(f"    • Alternatives considered")
        print(f"    • Decision rationale with confidence scores")
        print(f"    • Key insights and impact on hypothesis")
    else:
        print_warning("No reasoning data found - Nobel Phase 1 may not be active")
    
    print_header("🎉 TEST COMPLETE")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print_warning("\n\nTest interrupted by user")
    except Exception as e:
        print_error(f"\n\nTest failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
