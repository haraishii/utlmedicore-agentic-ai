"""Test add_manual_context + get_manual_episodes (direct Neo4j, no LLM)."""
import asyncio, datetime
from memory.patient_memory import PatientMemory

async def main():
    mem = PatientMemory('C5945F0F59FB_D612D9000180')

    # 1. Write a test entry
    ok = await mem.add_manual_context(
        content="Had nasi goreng + fried egg for dinner, approximately 600 kcal",
        context_type="meal",
        reference_time=datetime.datetime.now()
    )
    print(f"Write OK: {ok}")

    # 2. Read back
    eps = await mem.get_manual_episodes(limit=10)
    print(f"\nManual episodes found: {len(eps)}")
    for e in eps:
        print(f"  [{e['timestamp']}] {e['name']}: {e['content']}")

asyncio.run(main())
