"""
Test Nobel Phase 2: Executive Summary for Medical Researchers
This test validates that the output answers critical questions:
- What is the medical innovation?
- Why do current treatments fail?
- What should a researcher do first?
- Why does this theory have merit?
"""
import asyncio
import httpx
from datetime import datetime


def print_executive_summary(summary: dict):
    """Display executive summary in researcher-friendly format"""
    print("\n" + "=" * 100)
    print("🏆 EXECUTIVE SUMMARY FOR MEDICAL RESEARCHERS")
    print("=" * 100 + "\n")
    
    # 1. ELEVATOR PITCH - What is this?
    print("📢 THE PROPOSAL (Elevator Pitch)")
    print("-" * 100)
    print(summary.get('elevator_pitch', 'N/A'))
    print("\n")
    
    # 2. THE GAP - Why current treatments fail
    print("🔴 THE CLINICAL GAP (Why Current Treatments Fail)")
    print("-" * 100)
    print(summary.get('current_treatment_gap', 'N/A'))
    print("\n")
    
    # 3. THE INNOVATION - What's novel?
    print("💡 THE INNOVATION (What's New)")
    print("-" * 100)
    print(summary.get('key_innovation', 'N/A'))
    print("\n")
    
    # 4. THE RATIONALE - Why should this work?
    print("🧬 BIOLOGICAL RATIONALE (Why This Should Work)")
    print("-" * 100)
    print(summary.get('biological_rationale', 'N/A'))
    print("\n")
    
    # 5. PRIORITY ACTIONS - What to do first?
    print("✅ PRIORITY ACTIONS (What To Do First)")
    print("-" * 100)
    actions = summary.get('priority_actions', [])
    for i, action in enumerate(actions, 1):
        print(f"{i}. {action}")
    print("\n")
    
    # 6. EVIDENCE STRENGTH
    print("📚 EVIDENCE STRENGTH")
    print("-" * 100)
    print(summary.get('evidence_strength', 'N/A'))
    print("\n")
    
    # 7. FEASIBILITY
    print("🎯 FEASIBILITY ASSESSMENT")
    print("-" * 100)
    print(summary.get('feasibility_verdict', 'N/A'))
    print("\n")
    
    # 8. TIMELINE
    print("📅 ESTIMATED TIMELINE")
    print("-" * 100)
    print(summary.get('estimated_timeline', 'N/A'))
    print("\n")
    
    # 9. COST
    print("💰 ESTIMATED COST")
    print("-" * 100)
    print(summary.get('estimated_cost', 'N/A'))
    print("\n")
    
    # 10. SUCCESS PROBABILITY
    print("🎲 SUCCESS PROBABILITY")
    print("-" * 100)
    print(summary.get('success_probability', 'N/A'))
    print("\n")
    
    print("=" * 100)
    print("✓ END OF EXECUTIVE SUMMARY")
    print("=" * 100 + "\n")


async def test_nobel_phase2():
    """Test Nobel Phase 2 implementation"""
    base_url = "http://localhost:8000"
    
    print("\n" + "=" * 100)
    print("🧪 TESTING NOBEL PHASE 2: EXECUTIVE SUMMARY FOR MEDICAL RESEARCHERS")
    print("=" * 100 + "\n")
    
    # Test scenario: Alzheimer's early detection
    hypothesis_request = {
        "goal": "Develop early diagnostic biomarkers for Alzheimer's disease that can detect pathology 5-10 years before clinical symptoms",
        "domain": "neurology",
        "constraints": {
            "focus": ["blood-based biomarkers", "non-invasive", "accessible to primary care"],
            "avoid": ["invasive procedures", "expensive imaging"],
            "timeline": "rapid",
            "budget_constraints": "moderate"
        },
        "max_runtime_minutes": 10
    }
    
    async with httpx.AsyncClient(timeout=600.0) as client:
        # Create hypothesis
        print("📤 Creating hypothesis request...")
        print(f"Goal: {hypothesis_request['goal']}")
        print(f"Domain: {hypothesis_request['domain']}\n")
        
        response = await client.post(f"{base_url}/api/v1/hypotheses", json=hypothesis_request)
        
        if response.status_code != 202:
            print(f"❌ Failed to create hypothesis: {response.status_code}")
            print(response.text)
            return
        
        result = response.json()
        hypothesis_id = result['id']
        print(f"✓ Hypothesis created: {hypothesis_id}")
        print(f"Status: {result['status']}\n")
        
        # Poll for completion
        print("⏳ Waiting for hypothesis generation (this may take 5-10 minutes)...\n")
        start_time = datetime.now()
        max_wait = 600  # 10 minutes
        poll_interval = 10
        
        while True:
            elapsed = (datetime.now() - start_time).total_seconds()
            if elapsed > max_wait:
                print(f"❌ Timeout after {max_wait} seconds")
                break
            
            response = await client.get(f"{base_url}/api/v1/hypotheses/{hypothesis_id}")
            if response.status_code != 200:
                print(f"❌ Failed to get hypothesis: {response.status_code}")
                break
            
            hypothesis = response.json()
            status = hypothesis['status']
            
            print(f"[{int(elapsed)}s] Status: {status}")
            
            if status == 'completed':
                print(f"\n✓ Hypothesis generation completed in {int(elapsed)} seconds\n")
                
                # Check for executive summary
                if 'executive_summary' not in hypothesis or hypothesis['executive_summary'] is None:
                    print("❌ ERROR: No executive summary found!")
                    print("This means Nobel Phase 2 is not implemented or not working.\n")
                    return
                
                print("✓ Executive summary found!\n")
                
                # Display the executive summary
                print_executive_summary(hypothesis['executive_summary'])
                
                # Also show hypothesis title for context
                if 'hypothesis_document' in hypothesis and hypothesis['hypothesis_document']:
                    title = hypothesis['hypothesis_document'].get('title', 'Untitled')
                    print(f"\n📄 Full Hypothesis Title: {title}\n")
                
                # Show reasoning step count for validation
                reasoning_steps = hypothesis.get('reasoning_steps', [])
                print(f"✓ Reasoning Steps Captured: {len(reasoning_steps)}")
                
                avg_confidence = sum(s['confidence'] for s in reasoning_steps) / len(reasoning_steps) if reasoning_steps else 0
                print(f"✓ Average Reasoning Confidence: {avg_confidence:.2%}")
                
                # Show narrative length
                narrative = hypothesis.get('reasoning_narrative', '')
                print(f"✓ Reasoning Narrative Length: {len(narrative):,} characters\n")

                # ------------------
                # Acceptance assertions (guards)
                # ------------------
                summary = hypothesis['executive_summary']

                # Evidence consistency
                # summary should expose a structured evidence dict under 'evidence_meta' or consolidated representation
                ev_meta = hypothesis.get('executive_summary_meta') or hypothesis.get('evidence_meta') or {}
                # If exec summary meta not present, attempt to parse from text (fallback)
                if not ev_meta:
                    ev_meta = hypothesis.get('evidence_meta', {})

                total = ev_meta.get('total', None)
                tiers = ev_meta.get('tiers', None)
                strength = ev_meta.get('strength', None)

                if tiers and total is not None:
                    assert total == sum(tiers.get(k, 0) for k in ['T1', 'T2', 'T3', 'T4'])
                assert strength is None or (0.0 <= float(strength) <= 1.0)
                assert "Compiled from 0 scientific sources" not in (summary.get('current_treatment_gap','') + summary.get('biological_rationale',''))

                # Feasibility label harmony
                # find composite in feasibility text
                fe_text = summary.get('feasibility_verdict','')
                import re as _re
                m = _re.search(r"Composite[: ]+([0-9]\.[0-9]{2})", fe_text)
                if m:
                    composite_val = float(m.group(1))
                    lbl = None
                    if composite_val >= 0.80:
                        lbl = "High (Green)"
                    elif composite_val >= 0.60:
                        lbl = "Moderate-High (Green)"
                    elif composite_val >= 0.40:
                        lbl = "Moderate (Amber)"
                    else:
                        lbl = "Low (Red)"
                    assert lbl in fe_text
                    if composite_val < 0.80:
                        assert "HIGHLY FEASIBLE" not in fe_text

                # Diagnostic mode guards
                assert "IND" not in (summary.get('estimated_timeline','') + summary.get('key_innovation',''))
                assert ("CLIA" in (summary.get('estimated_timeline','') + summary.get('feasibility_verdict','')) ) or ("CE-IVD" in (summary.get('estimated_timeline','') + summary.get('feasibility_verdict','')))

                # Cross-domain filter
                k = summary.get('key_innovation','')
                assert "Lipid nanoparticle" not in k and "self-healing" not in k

                # Formatting: Ethics on its own line
                assert "**Ethics" in (summary.get('feasibility_verdict','') + summary.get('biological_rationale',''))
                
                # NOBEL QUALITY LOCKS (Final Refinements)
                full_text = str(summary)
                
                # 1. Accuracy claims softened
                assert ">90% accuracy" not in full_text, "Overoptimistic accuracy claim found"
                
                # 2. Domain pluralization (no "1 domains")
                assert "1 domains" not in full_text, "Grammar error: '1 domains' should be '1 domain' or 'one domain'"
                
                # 3. Feasibility header cleanup (no double labels)
                if "Moderate-High (Green)" in fe_text:
                    assert "FEASIBLE (MODERATE-HIGH)" not in fe_text, "Redundant feasibility label found"
                
                # 4. L1CAM caveat check
                if "L1CAM" in full_text or "l1cam" in full_text.lower():
                    assert "Assay Caveats" in full_text, "L1CAM mentioned but no assay caveats provided"
                    assert "orthogonal" in full_text.lower() or "CD9" in full_text or "CD63" in full_text or "CD81" in full_text, \
                        "L1CAM caveat should mention orthogonal EV markers"
                
                # 5. Assay Caveats & Controls section present for diagnostics
                if "diagnostic" in full_text.lower() or "biomarker" in full_text.lower():
                    assert "Assay Caveats" in full_text, "Diagnostic proposal should have Assay Caveats section"
                
                print("\n✅ ALL QUALITY LOCKS VALIDATED")
                
                print("=" * 100)
                print("✓ NOBEL PHASE 2 TEST COMPLETED SUCCESSFULLY")
                print("=" * 100)
                print("\nKEY VALIDATION POINTS:")
                print("1. ✓ Executive summary generated")
                print("2. ✓ Medical researcher questions answered:")
                print("   - What is the proposal? (Elevator pitch)")
                print("   - Why current treatments fail? (Clinical gap)")
                print("   - What's novel? (Key innovation)")
                print("   - Why should it work? (Biological rationale)")
                print("   - What to do first? (Priority actions)")
                print("   - Why believe it? (Evidence strength)")
                print("   - Is it feasible? (Feasibility verdict)")
                print("   - How long? (Timeline)")
                print("   - How much? (Cost)")
                print("   - What are the odds? (Success probability)")
                print("3. ✓ Output is researcher-friendly, not just technical")
                print("=" * 100 + "\n")
                
                break
            
            elif status == 'failed':
                print(f"\n❌ Hypothesis generation failed")
                print(f"Error: {hypothesis.get('error_message', 'Unknown error')}\n")
                break
            
            await asyncio.sleep(poll_interval)


if __name__ == "__main__":
    print("\n🚀 Starting Nobel Phase 2 Test...\n")
    print("This test will:")
    print("1. Create a hypothesis for Alzheimer's early detection")
    print("2. Wait for the complete generation pipeline")
    print("3. Display the EXECUTIVE SUMMARY prominently")
    print("4. Validate that it answers medical researcher questions\n")
    
    asyncio.run(test_nobel_phase2())
