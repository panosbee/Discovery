"""Quick import test for modified modules"""
import sys

print("Testing imports of modified modules...")

modules_to_test = [
    'medical_discovery.services.narrative_generator',
    'medical_discovery.services.orchestrator',
    'medical_discovery.agents.evidence_miner'
]

all_ok = True
for module in modules_to_test:
    try:
        __import__(module)
        print(f"✓ {module}")
    except Exception as e:
        print(f"✗ {module}: {e}")
        all_ok = False

if all_ok:
    print("\n✓ All imports successful!")
    sys.exit(0)
else:
    print("\n✗ Some imports failed!")
    sys.exit(1)
