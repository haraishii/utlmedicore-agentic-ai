"""End-to-end test: verify manual context timestamps are properly converted to UTC+8."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from memory.patient_memory import PatientMemory
from utils.tz_utils import utc_to_utc8

mem = PatientMemory('C5945F0F59FB_D612D9000180')
entries = mem.get_manual_episodes_sync(limit=10)

print(f"Total entries: {len(entries)}")
print("\nConverted timestamps (UTC+8):")
for e in entries:
    ts = utc_to_utc8(e.get('timestamp', ''))
    cat = e.get('name', 'unknown')
    if cat.startswith('meal'): cat = 'MEAL'
    elif cat.startswith('activity'): cat = 'ACTIVITY'
    content = e.get('content', '')[:60]
    print(f"  [{ts} UTC+8] [{cat}] {content}")
