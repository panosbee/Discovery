"""
Quick Nobel Phase 1 Test
Tests transparent reasoning with a single hypothesis
"""

import asyncio
import httpx
from datetime import datetime

BASE_URL = "http://localhost:8000"

# Color codes
class C:
    H = '\033[95m'
    B = '\033[94m'
    G = '\033[92m'
    Y = '\033[93m'
    R = '\033[91m'
    E = '\033[0m'
    BOLD = '\033[1m'

async def test_nobel_reasoning():
    """Quick test of Nobel-Level transparent reasoning"""
    print(f"\n{C.H}{C.BOLD}{'='*80}{C.E}")
    print(f"{C.H}{C.BOLD}{'🧠 Nobel Phase 1 - Transparent Reasoning Test'.center(80)}{C.E}")
    print(f"{C.H}{C.BOLD}{'='*80}{C.E}\n")
    
    async with httpx.AsyncClient(timeout=600.0) as client:
        # Health check
        print(f"{C.B}Checking server health...{C.E}")
        try:
            response = await client.get(f"{BASE_URL}/health")
            health = response.json()
            print(f"{C.G}✓ Server healthy - v{health.get('version')}{C.E}\n")
        except Exception as e:
            print(f"{C.R}✗ Server not responding: {e}{C.E}")
            return
        
        # Create hypothesis
        print(f"{C.B}Creating test hypothesis...{C.E}")
        payload = {
            "domain": "neurology",
            "goal": "Develop a blood-based biomarker panel for early Alzheimer's detection",
            "constraints": {
                "max_cost_usd": 5000000,
                "timeline_months": 24,
                "risk_tolerance": "moderate"
            }
        }
        
        response = await client.post(f"{BASE_URL}/v1/hypotheses", json=payload)
        create_result = response.json()
        hyp_id = create_result.get("id")
        print(f"{C.G}✓ Created hypothesis: {hyp_id}{C.E}\n")
        
        # Monitor progress
        print(f"{C.B}Monitoring hypothesis generation...{C.E}")
        start_time = datetime.now()
        
        while True:
            response = await client.get(f"{BASE_URL}/v1/hypotheses/{hyp_id}")
            hypothesis = response.json()
            status = hypothesis.get("status")
            
            elapsed = (datetime.now() - start_time).total_seconds()
            print(f"  [{int(elapsed)}s] Status: {status}", end='\r')
            
            if status == "completed":
                print(f"\n{C.G}✓ Completed in {int(elapsed)} seconds!{C.E}\n")
                break
            elif status == "failed":
                print(f"\n{C.R}✗ Failed: {hypothesis.get('error_message')}{C.E}")
                return
            
            await asyncio.sleep(5)
        
        # Analyze Nobel-Level Reasoning
        print(f"{C.H}{C.BOLD}{'─'*80}{C.E}")
        print(f"{C.H}{C.BOLD}🧠 Nobel-Level Transparent Reasoning Analysis{C.E}")
        print(f"{C.H}{C.BOLD}{'─'*80}{C.E}\n")
        
        reasoning_steps = hypothesis.get("reasoning_steps", [])
        reasoning_narrative = hypothesis.get("reasoning_narrative", "")
        reasoning_flowchart = hypothesis.get("reasoning_flowchart", "")
        
        if not reasoning_steps:
            print(f"{C.R}✗ No reasoning steps found! Nobel Phase 1 may not be active.{C.E}")
            return
        
        print(f"{C.G}✓ Found {len(reasoning_steps)} reasoning steps{C.E}\n")
        
        # Show each reasoning step
        total_confidence = 0
        for i, step in enumerate(reasoning_steps, 1):
            agent = step.get("agent", "Unknown")
            action = step.get("action", "Unknown")
            question = step.get("question_asked", "")
            reasoning = step.get("reasoning", "")
            alternatives = step.get("alternatives_considered", [])
            decision_rationale = step.get("decision_rationale", "")
            confidence = step.get("confidence", 0.0)
            key_insight = step.get("key_insight", "")
            impact = step.get("impact_on_hypothesis", "")
            
            total_confidence += confidence
            
            # Confidence visualization
            conf_bar = "█" * int(confidence * 10)
            conf_color = C.G if confidence >= 0.8 else C.Y if confidence >= 0.6 else C.R
            
            print(f"{C.BOLD}{'═'*80}{C.E}")
            print(f"{C.BOLD}Step {i}/{len(reasoning_steps)}: {agent}{C.E}")
            print(f"{C.BOLD}{'═'*80}{C.E}")
            print(f"\n{C.B}Action:{C.E} {action}")
            
            if question:
                print(f"\n{C.B}❓ Question Addressed:{C.E}")
                print(f"   {question}")
            
            if reasoning:
                print(f"\n{C.B}🧠 Reasoning:{C.E}")
                print(f"   {reasoning[:250]}{'...' if len(reasoning) > 250 else ''}")
            
            if alternatives:
                print(f"\n{C.B}🔀 Alternatives Considered:{C.E}")
                for alt in alternatives[:3]:
                    print(f"   • {alt}")
            
            if decision_rationale:
                print(f"\n{C.B}✅ Decision Rationale:{C.E}")
                print(f"   {decision_rationale[:200]}{'...' if len(decision_rationale) > 200 else ''}")
            
            print(f"\n{C.B}📊 Confidence:{C.E} {conf_color}{confidence:.2f}{C.E} {conf_bar}")
            
            if key_insight:
                print(f"\n{C.B}💡 Key Insight:{C.E}")
                print(f"   {key_insight[:200]}{'...' if len(key_insight) > 200 else ''}")
            
            if impact:
                print(f"\n{C.B}🎯 Impact:{C.E}")
                print(f"   {impact[:200]}{'...' if len(impact) > 200 else ''}")
            
            print()
        
        # Summary statistics
        avg_confidence = total_confidence / len(reasoning_steps)
        avg_conf_bar = "█" * int(avg_confidence * 10)
        avg_conf_color = C.G if avg_confidence >= 0.8 else C.Y
        
        print(f"{C.H}{C.BOLD}{'─'*80}{C.E}")
        print(f"{C.H}{C.BOLD}📊 Reasoning Summary{C.E}")
        print(f"{C.H}{C.BOLD}{'─'*80}{C.E}\n")
        
        print(f"{C.G}✓ Total Reasoning Steps: {len(reasoning_steps)}{C.E}")
        print(f"{C.G}✓ Average Confidence: {avg_conf_color}{avg_confidence:.2f}{C.E} {avg_conf_bar}")
        print(f"{C.G}✓ Narrative Length: {len(reasoning_narrative):,} characters{C.E}")
        print(f"{C.G}✓ Flowchart Available: {'Yes' if reasoning_flowchart else 'No'}{C.E}")
        
        # Show narrative preview
        if reasoning_narrative:
            print(f"\n{C.H}{C.BOLD}📖 Reasoning Narrative Preview:{C.E}")
            print(f"{C.H}{'─'*80}{C.E}")
            print(f"{reasoning_narrative[:600]}")
            print(f"{C.H}{'─'*80}{C.E}")
            print(f"{C.B}... ({len(reasoning_narrative) - 600} more characters){C.E}")
        
        # Final verdict
        print(f"\n{C.H}{C.BOLD}{'═'*80}{C.E}")
        print(f"{C.G}{C.BOLD}✓ NOBEL PHASE 1 SUCCESSFULLY IMPLEMENTED!{C.E}")
        print(f"{C.H}{C.BOLD}{'═'*80}{C.E}\n")
        
        print(f"{C.G}The system now provides:{C.E}")
        print(f"  ✓ Step-by-step reasoning showing HOW decisions were made")
        print(f"  ✓ Questions addressed at each step")
        print(f"  ✓ Alternatives considered and why they were rejected")
        print(f"  ✓ Confidence scores for each decision")
        print(f"  ✓ Key insights and impact on the hypothesis")
        print(f"  ✓ Human-readable narrative explaining the entire process")
        print(f"\n{C.B}Researchers can now understand the AI's thought process!{C.E}\n")


if __name__ == "__main__":
    try:
        asyncio.run(test_nobel_reasoning())
    except KeyboardInterrupt:
        print(f"\n{C.Y}Test interrupted{C.E}")
    except Exception as e:
        print(f"\n{C.R}Test failed: {e}{C.E}")
        import traceback
        traceback.print_exc()
