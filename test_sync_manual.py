"""Test sync manual context: add, list, delete — no async, no LLM lock."""
from memory.patient_memory import PatientMemory
import datetime

mem = PatientMemory('C5945F0F59FB_D612D9000180')

# 1. Add
ok = mem.add_manual_context_sync("Test sync entry - should always work", "meal", datetime.datetime.now())
print(f"1. Add: {ok}")

# 2. List
eps = mem.get_manual_episodes_sync(limit=20)
print(f"\n2. List: {len(eps)} entries")
for e in eps:
    print(f"   [{e['id'][:12]}...] {e['source']:8s} | {e['name']}: {e['content'][:50]}")

# 3. Delete the test entry we just created
if eps:
    test_id = eps[0]['id']
    ok2 = mem.delete_manual_context_sync(test_id)
    print(f"\n3. Delete '{test_id[:12]}...': {ok2}")
    
    # Verify it's gone
    eps2 = mem.get_manual_episodes_sync(limit=20)
    print(f"   After delete: {len(eps2)} entries")
