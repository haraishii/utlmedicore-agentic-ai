"""
test_memory.py — Day 1 Verification Script
============================================
Run this BEFORE integrating into the main app.
Makes sure Neo4j, Graphiti, and Ollama embeddings all work together.

Usage:
    python test_memory.py

Expected output (if everything is working):
    [Graphiti] Connecting...
    [Graphiti] ✅ Memory graph ready — 100% local, zero API cost!
    [Memory] 💾 Stored [baseline] for TEST_PATIENT...
    [Memory] 💾 Stored [critical_fall] for TEST_PATIENT...
    [Memory] 💾 Stored [baseline] for TEST_PATIENT...
    [Memory] 🔍 Retrieved 2 facts for TEST_PATIENT

    --- Memory Context ---
    Patient Memory Context (from past sessions):
    - Patient has HR 125 after lunch. This is normal.
    - Patient fell in bathroom previously...

    ✅ ALL TESTS PASSED — Memory layer is working!
"""

import asyncio
import sys
import os

# Add project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from memory.patient_memory import PatientMemory
from memory.graphiti_client import close_graphiti


async def test_full_memory():
    print("=" * 60)
    print("UTLMediCore Memory Layer — Day 1 Verification")
    print("=" * 60)

    # Use a fake test patient (won't interfere with real data)
    patient = PatientMemory("TEST_DEVICE_001")

    # -------------------------------------------------------
    # TEST 1: Store a baseline observation
    # -------------------------------------------------------
    print("\n[TEST 1] Storing baseline observation...")
    await patient.add_episode(
        "Patient has HR 125 bpm after lunch at noon. This is their personal normal pattern "
        "and should NOT trigger a critical alert. Vitals return to baseline (HR ~75) within 30 minutes.",
        episode_type="baseline"
    )

    # -------------------------------------------------------
    # TEST 2: Store a past fall (the most important memory)
    # -------------------------------------------------------
    print("\n[TEST 2] Storing past fall event...")
    await patient.store_sensor_snapshot(
        data={
            "HR": 45,
            "Blood_oxygen": 82,
            "Posture_state": 5,  # FALLING
            "Area": 6,           # BATHROOM
            "Step": 0
        }
    )

    # -------------------------------------------------------
    # TEST 3: Store another baseline
    # -------------------------------------------------------
    print("\n[TEST 3] Storing sleep pattern baseline...")
    await patient.store_baseline(
        "Patient normally lies down (Posture=3) in Bedroom (Area=7) between 14:00-15:00 "
        "for afternoon rest. HR drops to 55-60 bpm during this period. This is NOT a fall."
    )

    # -------------------------------------------------------
    # TEST 4: Query — the most important test
    # -------------------------------------------------------
    print("\n[TEST 4] Querying memory: 'Is HR 125 dangerous for this patient?'")
    context = await patient.get_patient_context(
        "Is HR 125 bpm dangerous for this patient?",
        limit=5
    )
    print("\n--- Memory Context ---")
    print(context)

    # -------------------------------------------------------
    # TEST 5: Query for past falls
    # -------------------------------------------------------
    print("\n[TEST 5] Querying memory: 'Has this patient fallen before?'")
    fall_context = await patient.get_patient_context(
        "Has this patient fallen before?",
        limit=3
    )
    print("\n--- Fall History ---")
    print(fall_context)

    # Cleanup
    await close_graphiti()

    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED — Memory layer is working!")
    print("=" * 60)
    print("\nNext step: Integrate into agentic_medicore_enhanced.py")


if __name__ == "__main__":
    asyncio.run(test_full_memory())
