"""Test: verify deduplication and UTC timestamp output."""
from memory.patient_memory import PatientMemory

mem = PatientMemory('C5945F0F59FB_D612D9000180')
eps = mem.get_manual_episodes_sync(limit=20)

print(f"Total (deduplicated): {len(eps)} entries\n")
for e in eps:
    print(f"  [{e['source']:8s}] {e['timestamp']}  |  {e['name']:20s}  |  {e['content'][:50]}")
