"""Quick check of failed hypothesis"""
import asyncio
from medical_discovery.data.mongo.client import mongodb_client

async def check():
    await mongodb_client.connect()
    coll = mongodb_client.get_collection('hypotheses')
    
    # Check failed hypothesis
    doc = await coll.find_one({'id': 'hyp_e3c5264b8b07'})
    if doc:
        print(f"Status: {doc.get('status')}")
        print(f"Error: {doc.get('error', 'None')}")
        print(f"Has hypothesis_document: {bool(doc.get('hypothesis_document'))}")
        print(f"Has evidence_packs: {len(doc.get('evidence_packs', []))}")
        print(f"Has cross_domain_transfers: {len(doc.get('cross_domain_transfers', []))}")
    else:
        print("Hypothesis not found")
    
    await mongodb_client.disconnect()

asyncio.run(check())
