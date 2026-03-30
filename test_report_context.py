"""Test: verify manual context is included in report prompt data."""
from memory.patient_memory import PatientMemory

mem = PatientMemory('C5945F0F59FB_D612D9000180')
entries = mem.get_manual_episodes_sync(limit=50)

print(f"Manual entries for report: {len(entries)}")
print("\nFormatted for AI prompt:")
for e in entries:
    ts = e.get('timestamp', '')[:16].replace('T', ' ')
    cat = e.get('name', 'unknown')
    if cat.startswith('meal'): cat = 'MEAL'
    elif cat.startswith('activity'): cat = 'ACTIVITY'
    elif cat.startswith('medical'): cat = 'MEDICAL RECORD'
    print(f"  - [{ts}] [{cat}] {e.get('content', '')}")
