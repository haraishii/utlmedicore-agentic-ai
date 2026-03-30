"""Verify all ManualContext entries now have an id (uuid or elementId fallback)."""
import asyncio
from memory.patient_memory import PatientMemory

async def main():
    mem = PatientMemory('C5945F0F59FB_D612D9000180')
    eps = await mem.get_manual_episodes(limit=20)
    print(f"Total entries: {len(eps)}")
    for e in eps:
        has_id = "OK" if e['id'] else "MISSING"
        print(f"  [{has_id}] id={e['id'][:20]}... | {e['source']} | {e['name']}: {e['content'][:40]}")

asyncio.run(main())
