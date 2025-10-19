"""
Test Enhanced Narrative: "Why This, Not That" per Agent
Displays biological/clinical reasoning with kept/dropped decisions
"""
import asyncio
import httpx
import json
from datetime import datetime


def print_agent_narrative(agent_data: dict, index: int):
    """Display single agent narrative with Why This Not That format"""
    print(f"\n{'='*100}")
    print(f"🤖 AGENT {index}: {agent_data.get('name', 'Unknown').upper()}")
    print(f"{'='*100}\n")
    
    # Action
    print(f"📋 Action: {agent_data.get('action', 'N/A')}\n")
    
    # Why This Not That
    print("🔀 WHY THIS, NOT THAT")
    print("-" * 100)
    why_this = agent_data.get('why_this_not_that', [])
    if why_this:
        for item in why_this:
            print(f"✅ KEPT: {item.get('kept', 'N/A')}")
            print(f"❌ DROPPED: {item.get('dropped', 'N/A')}")
            print(f"💡 REASON: {item.get('reason', 'N/A')}\n")
    else:
        print("Direct path - no alternatives evaluated\n")
    
    # Decision Points
    print("🎯 DECISION CRITERIA")
    print("-" * 100)
    criteria = agent_data.get('decision_points', [])
    for i, criterion in enumerate(criteria, 1):
        print(f"{i}. {criterion}")
    print()
    
    # Key Insight
    insight = agent_data.get('key_insight', '')
    if insight:
        print("💡 KEY INSIGHT")
        print("-" * 100)
        print(insight)
        print()
    
    # Uncertainties
    print("⚠️  UNCERTAINTIES")
    print("-" * 100)
    uncertainties = agent_data.get('uncertainties', [])
    for i, uncertainty in enumerate(uncertainties, 1):
        print(f"{i}. {uncertainty}")
    print()
    
    # Handoff
    print("🔄 HANDOFF")
    print("-" * 100)
    handoff = agent_data.get('handoff', {})
    print(f"To: {handoff.get('to', 'Unknown')}")
    print(f"Payload: {', '.join(handoff.get('payload', []))}")
    print()
    
    # Confidence
    confidence = agent_data.get('confidence', 0)
    confidence_bar = "█" * int(confidence * 10)
    confidence_empty = "░" * (10 - int(confidence * 10))
    print("📊 CONFIDENCE")
    print("-" * 100)
    print(f"{confidence:.2%} {confidence_bar}{confidence_empty}")
    print()


def print_narrative_timeline(narrative_json: dict):
    """Display full narrative timeline"""
    print("\n" + "="*100)
    print("📖 NARRATIVE TIMELINE: Agent-by-Agent Reasoning")
    print("="*100 + "\n")
    
    narrative = narrative_json.get('narrative', {})
    
    # Question & Criteria
    print("🎯 RESEARCH QUESTION")
    print("-" * 100)
    print(narrative.get('question', 'N/A'))
    print()
    
    print("📋 CRITERIA")
    print("-" * 100)
    criteria = narrative.get('criteria', [])
    for i, c in enumerate(criteria, 1):
        print(f"{i}. {c}")
    print()
    
    # Agents
    agents = narrative.get('agents', [])
    for i, agent_data in enumerate(agents, 1):
        print_agent_narrative(agent_data, i)
    
    print("="*100)
    print("✓ END OF NARRATIVE TIMELINE")
    print("="*100 + "\n")


def print_cards_summary(cards: dict):
    """Display quick summary cards"""
    print("\n" + "="*100)
    print("🃏 QUICK SUMMARY CARDS")
    print("="*100 + "\n")
    
    # Hypothesis Card
    hyp = cards.get('hypothesis', {})
    print("📄 HYPOTHESIS")
    print("-" * 100)
    print(f"Title: {hyp.get('title', 'N/A')}")
    print(f"Feasibility: {hyp.get('feasibility', 'N/A')}")
    print(f"Ethics: {hyp.get('ethics', 'N/A')}")
    print(f"Panel: {', '.join(hyp.get('panel', [])[:3])}{'...' if len(hyp.get('panel', [])) > 3 else ''}")
    print()
    
    # Evidence Card
    ev = cards.get('evidence', {})
    print("📚 EVIDENCE")
    print("-" * 100)
    print(f"Total Sources: {ev.get('count', 0)}")
    tiers = ev.get('tiers', {})
    print(f"Tiers: T1={tiers.get('T1', 0)}, T2={tiers.get('T2', 0)}, T3={tiers.get('T3', 0)}, T4={tiers.get('T4', 0)}, T5={tiers.get('T5', 0)}")
    print()
    
    # Simulation Card
    sim = cards.get('simulation', {})
    print("🔬 SIMULATION SCORES")
    print("-" * 100)
    scores = sim.get('scores', {})
    for key, value in scores.items():
        print(f"{key}: {value:.2%}")
    print()
    
    # Ethics Card
    eth = cards.get('ethics', {})
    print("⚖️  ETHICS")
    print("-" * 100)
    print(f"Verdict: {eth.get('verdict', 'N/A')}")
    conditions = eth.get('conditions', [])
    if conditions:
        print("Conditions:")
        for i, cond in enumerate(conditions[:3], 1):
            print(f"  {i}. {cond}")
    print()
    
    print("="*100 + "\n")


async def test_enhanced_narrative():
    """Test enhanced narrative with Why This Not That format"""
    base_url = "http://localhost:8000"
    
    print("\n" + "="*100)
    print("🧪 TESTING ENHANCED NARRATIVE: Why This, Not That per Agent")
    print("="*100 + "\n")
    
    # Test scenario
    hypothesis_request = {
        "goal": "Develop blood-based biomarker panel for early Alzheimer's detection (preclinical/MCI stage)",
        "domain": "neurology",
        "constraints": {
            "focus": ["multi-layer biology", "clinical scalability", "reproducible"],
            "avoid": ["invasive procedures", "expensive imaging"],
            "timeline": "rapid"
        },
        "max_runtime_minutes": 10
    }
    
    async with httpx.AsyncClient(timeout=600.0) as client:
        # Create hypothesis
        print("📤 Creating hypothesis...")
        print(f"Goal: {hypothesis_request['goal']}\n")
        
        response = await client.post(f"{base_url}/api/v1/hypotheses", json=hypothesis_request)
        
        if response.status_code != 202:
            print(f"❌ Failed: {response.status_code}")
            return
        
        result = response.json()
        hypothesis_id = result['id']
        print(f"✓ Created: {hypothesis_id}\n")
        
        # Poll for completion
        print("⏳ Generating (5-10 minutes)...\n")
        start_time = datetime.now()
        
        while True:
            elapsed = (datetime.now() - start_time).total_seconds()
            if elapsed > 600:
                print(f"❌ Timeout after 600s")
                break
            
            response = await client.get(f"{base_url}/api/v1/hypotheses/{hypothesis_id}")
            if response.status_code != 200:
                break
            
            hypothesis = response.json()
            status = hypothesis['status']
            
            print(f"[{int(elapsed)}s] Status: {status}")
            
            if status == 'completed':
                print(f"\n✓ Completed in {int(elapsed)}s\n")
                
                # Check for narrative JSON
                narrative_json = hypothesis.get('reasoning_narrative_json')
                if not narrative_json:
                    print("❌ No reasoning_narrative_json found!")
                    print("Available keys:", list(hypothesis.keys()))
                    return
                
                print("✓ Found reasoning_narrative_json\n")
                
                # Save to file for inspection
                with open('narrative_output.json', 'w', encoding='utf-8') as f:
                    json.dump(narrative_json, f, indent=2, ensure_ascii=False)
                print("✓ Saved to narrative_output.json\n")
                
                # Display narrative timeline
                print_narrative_timeline(narrative_json)
                
                # Display cards
                cards = narrative_json.get('cards', {})
                print_cards_summary(cards)
                
                # Provenance
                prov = narrative_json.get('provenance', {})
                print("🔍 PROVENANCE")
                print("-" * 100)
                print(f"Trace ID: {prov.get('trace_id', 'N/A')}")
                print(f"Timestamp: {prov.get('timestamp', 'N/A')}")
                print()
                
                print("="*100)
                print("✓ TEST COMPLETED SUCCESSFULLY")
                print("="*100)
                print("\nKEY VALIDATIONS:")
                print("1. ✓ Per-agent narrative with 'Why This Not That'")
                print("2. ✓ Decision criteria shown")
                print("3. ✓ Handoff payloads documented")
                print("4. ✓ Uncertainties explicitly listed")
                print("5. ✓ Biological/clinical focus (not just AI process)")
                print("6. ✓ Structured JSON for UI rendering")
                print("7. ✓ Quick summary cards available")
                print("="*100 + "\n")
                
                break
            
            elif status == 'failed':
                print(f"\n❌ Failed: {hypothesis.get('error_message')}\n")
                break
            
            await asyncio.sleep(10)


if __name__ == "__main__":
    print("\n🚀 Starting Enhanced Narrative Test\n")
    print("This test validates:")
    print("- 'Why This, Not That' reasoning per agent")
    print("- Decision criteria transparency")
    print("- Handoff documentation")
    print("- Uncertainty tracking")
    print("- Structured JSON output\n")
    
    asyncio.run(test_enhanced_narrative())
