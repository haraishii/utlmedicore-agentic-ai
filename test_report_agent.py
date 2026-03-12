"""Quick test of Lite Agent narrative output"""
import sys, os
sys.path.insert(0, r'e:\agentic')
from dotenv import load_dotenv
load_dotenv(r'e:\agentic\.env')

from insights.lite_report_agent import generate_lite_narrative
import json

print("[INFO] Testing Lite Agent with sample patient data...")

sample_vitals = {"heart_rate": {"average": 72.5, "minimum": 60, "maximum": 95, "readings_count": 68}, "blood_oxygen": {"average": 97.2, "minimum": 94, "hypoxia_events": 0, "readings_count": 68}}
sample_acts = {"most_common_activity": "Sitting", "total_readings": 68, "distribution": {"Sitting": "62%", "Standing": "38%"}}
sample_locs = {"most_visited": "Living Room", "locations_visited": 3, "distribution": {"Living Room": 42, "Bedroom": 39, "Unknown Area": 8}}
sample_alerts = {"total_alerts": 0, "critical_alerts": [], "warning_alerts": []}
sample_graph = "ACTIVITY DURATION SUMMARY for Patient DCA632971FC3: Based on 68 recorded snapshots. Monitoring period: 2026-03-12 12:57 to 2026-03-12 14:27 (1.5 hours total) Time spent in each posture: Sitting: 42 min Standing: 33 min Time spent in each location: Living Room: 42 min Bedroom: 28 min Unknown Area: 4 min Step count - avg: 7,122, max recorded: 7,122"

# Build model_caller using the running app's configured model
OLLAMA_CLOUD_API_KEY = os.getenv('OLLAMA_CLOUD_API_KEY', '')
MODEL = os.getenv('COORDINATOR_AGENT_MODEL', '')

def model_caller(prompt):
    if OLLAMA_CLOUD_API_KEY:
        from ollama import Client
        client = Client(
            host='https://ollama.com',
            headers={'Authorization': f'Bearer {OLLAMA_CLOUD_API_KEY}'}
        )
        # Try cloud models that are available
        for model_name in ['deepseek-v3', 'gemma3:4b', 'llama3.2']:
            try:
                resp = client.chat(model=model_name, messages=[{"role": "user", "content": prompt}], stream=False)
                print(f"  [model used: {model_name}]")
                return resp.message.content
            except Exception as e:
                if '404' in str(e):
                    continue
                raise
    # Local fallback
    from ollama import Client
    client = Client()
    resp = client.chat(model='lfm2.5-thinking:1.2b', messages=[{"role": "user", "content": prompt}], stream=False)
    return resp.message.content

print(f"[INFO] Using cloud key: {'YES' if OLLAMA_CLOUD_API_KEY else 'NO'}")
print("[INFO] Calling generate_lite_narrative... (may take ~30-60s)")

result = generate_lite_narrative(
    patient_id="DCA632971FC3",
    vital_signs=sample_vitals,
    activities=sample_acts,
    locations=sample_locs,
    alerts=sample_alerts,
    risk_score=0.0,
    graphiti_summary=sample_graph,
    time_range_hours=24,
    model_caller=model_caller
)
print("\n=== LITE AGENT OUTPUT ===")
print(result)
print("=========================")
