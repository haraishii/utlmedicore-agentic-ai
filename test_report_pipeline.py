"""
Final verification: Full report data pipeline test.
Tests: activity_summary (graph), manual context, and report generation data assembly.
"""
import sys, os, asyncio
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from memory.patient_memory import PatientMemory

DEVICE_ID = 'C5945F0F59FB_D612D9000180'
mem = PatientMemory(DEVICE_ID)

print("=" * 70)
print("TEST 1: Graph Activity Summary (Sensor Data)")
print("=" * 70)
try:
    summary = asyncio.run(mem.get_activity_summary(24))
    if summary:
        print(f"  OK: {len(summary)} chars")
        print(f"  Preview: {summary[:200]}...")
    else:
        print("  WARNING: Empty summary (no sensor data in last 24h)")
except Exception as e:
    print(f"  FAILED: {e}")

print()
print("=" * 70)
print("TEST 2: Manual Context Entries")
print("=" * 70)
try:
    entries = mem.get_manual_episodes_sync(limit=50)
    print(f"  OK: {len(entries)} entries found")
    for e in entries:
        ts = e.get('timestamp', '')[:16].replace('T', ' ')
        cat = e.get('name', 'unknown')
        if cat.startswith('meal'): cat = 'MEAL'
        elif cat.startswith('activity'): cat = 'ACTIVITY'
        elif cat.startswith('medical'): cat = 'MEDICAL RECORD'
        print(f"    - [{ts}] [{cat}] {e.get('content', '')[:60]}")
except Exception as e:
    print(f"  FAILED: {e}")

print()
print("=" * 70)
print("TEST 3: Combined AI Prompt Simulation")
print("=" * 70)
try:
    summary = asyncio.run(mem.get_activity_summary(24))
    entries = mem.get_manual_episodes_sync(limit=50)
    
    # Build manual text like the report endpoint does
    manual_text = ""
    if entries:
        lines = []
        for entry in entries:
            ts = entry.get('timestamp', '')[:16].replace('T', ' ')
            category = entry.get('name', 'unknown')
            if category.startswith('meal'): category = 'MEAL'
            elif category.startswith('activity'): category = 'ACTIVITY'
            elif category.startswith('medical'): category = 'MEDICAL RECORD'
            lines.append(f"- [{ts}] [{category}] {entry.get('content', '')}")
        manual_text = "\n".join(lines)
    
    print(f"  Sensor data:  {'YES' if summary else 'NO'} ({len(summary)} chars)")
    print(f"  Manual logs:  {'YES' if manual_text else 'NO'} ({len(entries)} entries)")
    print()
    print("  --- What the AI will see ---")
    print(f"  SENSOR DATA SUMMARY:")
    print(f"  {summary[:300] if summary else 'No sensor data'}...")
    print()
    print(f"  MANUAL PATIENT LOGS:")
    print(f"  {manual_text}")
    print("  --- END ---")
except Exception as e:
    print(f"  FAILED: {e}")

print()
print("=" * 70)
print("TEST 4: CrewAI Import Check")
print("=" * 70)
try:
    from insights.report_crew import get_report_crew
    crew = get_report_crew()
    print(f"  CrewAI OK: model={crew.llm.model}")
    print(f"  generate_narrative accepts manual_context: {'manual_context' in crew.generate_narrative.__code__.co_varnames}")
except Exception as e:
    print(f"  CrewAI NOT available: {e}")
    try:
        from insights.lite_report_agent import generate_lite_narrative
        import inspect
        sig = inspect.signature(generate_lite_narrative)
        print(f"  Lite Agent OK: params={list(sig.parameters.keys())}")
    except Exception as e2:
        print(f"  Lite Agent also failed: {e2}")

print()
print("ALL VERIFICATION COMPLETE")
