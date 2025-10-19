"""
Test script to create a hypothesis and verify all connectors
"""
import httpx
import json
import time
import asyncio


async def test_hypothesis():
    """Test hypothesis creation"""
    
    # Create hypothesis
    print("🚀 Creating hypothesis...")
    
    request_data = {
        "domain": "diabetes",
        "goal": "Discover novel therapeutic targets for type 2 diabetes using multi-omics approaches",
        "constraints": {
            "focus": [
                "Focus on druggable targets",
                "Consider patient stratification",
                "Prioritize targets with clinical validation potential"
            ],
            "avoid": ["Known toxicity pathways"],
            "timeline": "standard"
        },
        "prior_knowledge": [
            "GLP-1 receptor agonists are effective",
            "Metformin is first-line treatment",
            "SGLT2 inhibitors provide cardiovascular benefits"
        ]
    }
    
    async with httpx.AsyncClient(timeout=300.0) as client:
        # Create hypothesis
        response = await client.post(
            "http://localhost:8000/v1/hypotheses",
            json=request_data
        )
        
        if response.status_code == 202:
            result = response.json()
            hypothesis_id = result.get("id") or result.get("hypothesis_id")
            
            if not hypothesis_id:
                print(f"❌ No hypothesis ID in response")
                print(f"Response: {json.dumps(result, indent=2)}")
                return
            
            print(f"✅ Hypothesis created: {hypothesis_id}")
            print(f"📊 Status: {result.get('status', 'unknown')}")
            print(f"💬 Message: {result.get('message', '')}")
            print(f"🔗 URL: http://localhost:8000/v1/hypotheses/{hypothesis_id}")
            
            # Wait a bit for background processing
            print("\n⏳ Waiting for background processing...")
            await asyncio.sleep(3)
            
            # Check status
            print("\n📋 Checking hypothesis status...")
            status_response = await client.get(
                f"http://localhost:8000/v1/hypotheses/{hypothesis_id}"
            )
            
            if status_response.status_code == 200:
                hypothesis_data = status_response.json()
                print(f"✅ Current status: {hypothesis_data['status']}")
                
                if hypothesis_data['status'] == 'completed':
                    print("\n🎉 Hypothesis generation completed!")
                    print(f"\n📝 Concept Map:")
                    print(json.dumps(hypothesis_data.get('concept_map', {}), indent=2)[:500])
                    
                    print(f"\n📚 Evidence Packs: {len(hypothesis_data.get('evidence_packs', []))} sources")
                    for pack in hypothesis_data.get('evidence_packs', [])[:5]:
                        print(f"  - {pack['source']}: {pack['title'][:80]}")
                    
                    print(f"\n📄 Hypothesis Document:")
                    doc = hypothesis_data.get('hypothesis_document', {})
                    print(f"  Title: {doc.get('title', 'N/A')}")
                    print(f"  Abstract: {doc.get('abstract', 'N/A')[:200]}...")
                    
                    print(f"\n⚖️ Ethics Validation: {hypothesis_data.get('ethics_report', {}).get('overall_compliance', 'N/A')}")
                    
                elif hypothesis_data['status'] == 'running':
                    print("⚙️ Hypothesis is still being generated...")
                    print("   This process uses 10 data connectors and may take several minutes")
                    
                elif hypothesis_data['status'] == 'failed':
                    print(f"❌ Hypothesis generation failed: {hypothesis_data.get('error')}")
                
            else:
                print(f"❌ Failed to get status: {status_response.status_code}")
        else:
            print(f"❌ Failed to create hypothesis: {response.status_code}")
            print(response.text)


async def test_health():
    """Test health endpoint"""
    print("\n🏥 Testing health endpoint...")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get("http://localhost:8000/health")
        
        if response.status_code == 200:
            health = response.json()
            print(f"✅ Health check passed")
            print(f"   Status: {health.get('status', 'unknown')}")
            print(f"   MongoDB: {health.get('mongodb_status', health.get('mongodb', 'N/A'))}")
            print(f"   Version: {health.get('version', 'N/A')}")
            print(f"   Full response: {json.dumps(health, indent=2)}")
        else:
            print(f"❌ Health check failed: {response.status_code}")


if __name__ == "__main__":
    print("=" * 60)
    print("🧪 Medical Discovery Platform - Test Suite")
    print("=" * 60)
    
    asyncio.run(test_health())
    print()
    asyncio.run(test_hypothesis())
    
    print("\n" + "=" * 60)
    print("✅ Test completed!")
    print("=" * 60)
