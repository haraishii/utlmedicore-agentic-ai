"""
Full End-to-End Test: Manual Entry → Read Back → Report Context
Uses the aisuite-agent environment
"""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from memory.patient_memory import PatientMemory

DEVICE_ID = 'C5945F0F59FB_D612D9000180'
mem = PatientMemory(DEVICE_ID)

print("=" * 70)
print("STEP 1: Write a test manual entry")
print("=" * 70)
try:
    result = mem.add_manual_context_sync(
        context_type="meal",
        content="[E2E TEST] Had oatmeal with honey and a banana for breakfast",
        reference_time="2026-03-26T06:30:00"
    )
    print(f"  Write result: {result}")
except Exception as e:
    print(f"  Write FAILED: {e}")

print()
print("=" * 70)
print("STEP 2: Read back all manual entries")
print("=" * 70)
try:
    entries = mem.get_manual_episodes_sync(limit=20)
    print(f"  Total entries: {len(entries)}")
    for i, e in enumerate(entries):
        print(f"  [{i+1}] [{e['source']:8s}] {e['timestamp'][:19]}  |  {e['name']:20s}  |  {e['content'][:60]}")
except Exception as e:
    print(f"  Read FAILED: {e}")

print()
print("=" * 70)
print("STEP 3: Build AI prompt context (what CrewAI/AI will see)")
print("=" * 70)
try:
    entries = mem.get_manual_episodes_sync(limit=50)
    lines = []
    for entry in entries:
        ts = entry.get('timestamp', '')[:16].replace('T', ' ')
        category = entry.get('name', 'unknown')
        if category.startswith('meal'): category = 'MEAL'
        elif category.startswith('activity'): category = 'ACTIVITY'
        elif category.startswith('medical'): category = 'MEDICAL RECORD'
        lines.append(f"- [{ts}] [{category}] {entry.get('content', '')}")
    manual_context_text = "\n".join(lines)
    
    print("  --- MANUAL PATIENT LOGS (sent to CrewAI) ---")
    print(manual_context_text)
    print("  --- END ---")
    print(f"\n  Total entries for report: {len(entries)}")
except Exception as e:
    print(f"  Context build FAILED: {e}")

print()
print("=" * 70)
print("STEP 4: Clean up test entry")
print("=" * 70)
try:
    entries = mem.get_manual_episodes_sync(limit=50)
    for e in entries:
        if "[E2E TEST]" in e.get('content', ''):
            deleted = mem.delete_manual_context_sync(e['id'])
            print(f"  Deleted test entry: {deleted} (id={e['id'][:20]}...)")
except Exception as e:
    print(f"  Cleanup FAILED: {e}")

print()
print("ALL STEPS COMPLETE")
