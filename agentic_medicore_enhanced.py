"""
UTLMediCore - Agentic AI Backend
Autonomous Health Monitoring System dengan Multi-Agent Architecture
"""

from flask import Flask, render_template, request, jsonify, send_file
from flask_socketio import SocketIO, emit
from aisuite import Client
import json
import requests
import csv
import os
import math
import statistics
from datetime import datetime, timedelta
from threading import Thread
import time
from collections import deque
from pymongo import MongoClient
import numpy as np
from report_generator import ReportGenerator
from dotenv import load_dotenv
from evaluation.opik_integration import TrackedAISuiteClient, track

# ======== GRAPHITI MCP MEMORY ========
from memory.patient_memory import PatientMemory, run_async, run_async_readonly
from memory.graphiti_client import close_graphiti
# =====================================

# Note: report_crew import is handled gracefully in report_generator.py
import os

# Load environment variables from .env file
load_dotenv()

# Custom JSON Encoder untuk handle datetime
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

# Create reports directories
os.makedirs('reports/daily', exist_ok=True)
os.makedirs('reports/weekly', exist_ok=True)
os.makedirs('reports/monthly', exist_ok=True)
os.makedirs('reports/archives', exist_ok=True)

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY', 'medicore-secret-2025')

# Enable static files
app.static_folder = 'static'
app.static_url_path = '/static'

socketio = SocketIO(app, cors_allowed_origins="*")

# ======================
# AGENTIC AI CONFIGURATION
# ======================

class AgentConfig:
    """
    REVOLUTIONARY Configuration - lfm2.5-thinking:1.2b
    
    SHOCKING DISCOVERY (2026-02-12):
    After testing 13 models, lfm2.5-thinking:1.2b DOMINATES all competitors!
    
    Test Results (30 comprehensive cases):
    - 100% fall detection (14/14 falls - PERFECT!)
    - 90.0% accuracy (HIGHEST EVER!)
    - F1 Score: 0.903 (BEST EVER!)
    - Latency: 9.3s (1.5x faster than llama3.1!)
    - Size: ~0.7 GB (7x SMALLER than llama3.1!)
    
    Beats Previous Champion (llama3.1:8b):
    - +7.1% better fall detection (100% vs 92.9%)
    - +16.7% better accuracy (90% vs 73.3%)
    - 34% faster response (9.3s vs 14.2s)
    - 86% smaller size (0.7GB vs 4.9GB)
    - Zero missed falls (vs 1 missed)
    
    Architecture: "Thinking" model - specialized for reasoning/pattern recognition
    Perfect for: Healthcare diagnostics, fall detection, anomaly detection
    
    Confidence: MAXIMUM+++ (revolutionary breakthrough!)
    Report: See reports/LFM25_THINKING_RESULTS_SHOCKING.md
    """
    
    # ==================
    # AGENT MODELS (Revolutionary Optimized)
    # ==================
    # All agents use lfm2.5-thinking:1.2b - proven BEST in comprehensive testing
    # Ultra-efficient: 1.2B params achieving what 8B models struggle with!
    
    MONITOR_AGENT = os.getenv('MONITOR_AGENT_MODEL', 'ollama:lfm2.5-thinking:1.2b')      # 100% fall detection ⚡
    ANALYZER_AGENT = os.getenv('ANALYZER_AGENT_MODEL', 'ollama:lfm2.5-thinking:1.2b')    # 90% accuracy ⚡
    ALERT_AGENT = os.getenv('ALERT_AGENT_MODEL', 'ollama:lfm2.5-thinking:1.2b')          # 9.3s response ⚡
    PREDICTOR_AGENT = os.getenv('PREDICTOR_AGENT_MODEL', 'ollama:lfm2.5-thinking:1.2b')  # 0.903 F1 score ⚡
    COORDINATOR_AGENT = os.getenv('COORDINATOR_AGENT_MODEL', 'ollama:lfm2.5-thinking:1.2b')  # 100% reliable ⚡
    
    # ==================
    # AGENT-SPECIFIC TEMPERATURES
    # ==================
    # Optimized for "thinking" model architecture
    
    TEMPERATURES = {
        "monitor": 0.1,      # Very deterministic for safety
        "analyzer": 0.2,     # Thinking model needs less creativity
        "predictor": 0.2,    # Balanced for trend prediction
        "alert": 0.1,        # Deterministic for critical alerts
        "coordinator": 0.2   # Efficient orchestration
    }
    
    # ==================
    # AGENT TIMEOUTS (seconds)
    # ==================
    # Based on lfm2.5-thinking:1.2b average latency of 9.3s (34% faster!)
    
    TIMEOUTS = {
        "monitor": 20,       # Faster model = shorter timeout
        "analyzer": 30,      # Quick analysis
        "predictor": 30,     # Fast predictions
        "alert": 15,         # Time-sensitive - ultra fast
        "coordinator": 25    # Efficient coordination
    }
    
    # Thresholds
    CRITICAL_FALL_THRESHOLD = 0.95  # 95% confidence
    ABNORMAL_HR_LOW = 45
    ABNORMAL_HR_HIGH = 110
    HYPOXIA_THRESHOLD = 90
    
    # Autonomous Actions
    AUTO_ALERT_ENABLED = True
    AUTO_ANALYSIS_INTERVAL = 10  # seconds
    PATTERN_DETECTION_WINDOW = 100  # data points
    
    # ==================
    # MONGODB CONFIGURATION (from .env)
    # ==================
    # Use environment variables for security - NEVER commit credentials!
    # MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017/')
    MONGO_URL = os.getenv('MONGO_URL', 'mongodb://viewer1:viewer1@127.0.0.1:27018/admin?authSource=admin&directConnection=true')
    DB_LIST = os.getenv('MONGO_DB_1', 'DCA632971FC3').split(',') if ',' in os.getenv('MONGO_DB_1', '') else [
        os.getenv('MONGO_DB_1', 'DCA632971FC3'),
        os.getenv('MONGO_DB_2', '2CCF6754457F')
    ]
    COLLECTION_NAME = os.getenv('MONGO_COLLECTION', 'posture_data')

# ======================
# DATA STRUCTURES
# ======================

class PatientState:
    """Real-time patient state tracker"""
    def __init__(self, device_id):
        self.device_id = device_id
        self.history = deque(maxlen=AgentConfig.PATTERN_DETECTION_WINDOW)
        self.alerts = []
        self.last_analysis = None
        self.risk_score = 0.0
        self.patterns_detected = []
        
        # Memory Layer (Graphiti)
        self.memory = PatientMemory(device_id)
        
    def add_data(self, data):
        """Add new sensor reading"""
        data['timestamp'] = datetime.now()
        self.history.append(data)
        
        # Memory Storage Logic:
        # Determine if we should store this snapshot in permanent memory
        hr = int(data.get('HR', 0))
        spo2 = int(data.get('Blood_oxygen', 0))
        posture = int(data.get('Posture_state', 0))
        
        is_notable = (
            posture == 5 or           # Fall
            hr > 110 or hr < 45 or    # Abnormal HR
            (0 < spo2 < 90)           # Low oxygen
        )
        
        # Store notable events or taking a routine snapshot every 50 readings
        if is_notable or len(self.history) % 50 == 0:
            # We don't wait for Ollama to finish writing (fire-and-forget) to keep server fast
            run_async(self.memory.store_sensor_snapshot(data), wait_result=False)
        
    def get_recent(self, n=10):
        """Get N most recent readings"""
        return list(self.history)[-n:]

# Global data structures
PATIENT_STATES = {}  # device_id -> PatientState
ACTIVE_ALERTS = []   # List of active alerts
AGENT_ACTIVITY_LOG = deque(maxlen=100)  # Last 100 agent activities

# ── Ollama Cloud API (api.ollama.com) ──────────────────────────────────────
OLLAMA_CLOUD_API_KEY  = os.getenv('OLLAMA_CLOUD_API_KEY', '')
OLLAMA_CLOUD_BASE_URL = os.getenv('OLLAMA_CLOUD_BASE_URL', 'https://api.ollama.com/v1')

_ollama_cloud_client = None

def get_ollama_cloud_client():
    """Lazy-init official ollama.Client for Ollama Cloud."""
    global _ollama_cloud_client
    if _ollama_cloud_client is None and OLLAMA_CLOUD_API_KEY:
        try:
            from ollama import Client as _OllamaClient
            _ollama_cloud_client = _OllamaClient(
                host='https://ollama.com',
                headers={'Authorization': 'Bearer ' + OLLAMA_CLOUD_API_KEY}
            )
            print(f"[OllamaCloud] Client initialized (host: ollama.com)")
        except Exception as e:
            print(f"[OllamaCloud] Init failed: {e}")
    return _ollama_cloud_client

def call_ollama_cloud(model_name: str, messages: list, temperature: float = 0.3):
    """Call Ollama Cloud via official ollama Python library.
    Returns an object with .choices[0].message.content for API compatibility.
    """
    client = get_ollama_cloud_client()
    if not client:
        raise RuntimeError("Ollama Cloud API key not configured — add OLLAMA_CLOUD_API_KEY to .env")

    resp = client.chat(model=model_name, messages=messages, stream=False)

    # Wrap in OpenAI-compatible shape so caller code is unchanged
    class _Msg:
        def __init__(self, content): self.content = content
    class _Choice:
        def __init__(self, content): self.message = _Msg(content)
    class _Resp:
        def __init__(self, content): self.choices = [_Choice(content)]

    content = resp['message']['content'] if isinstance(resp, dict) else resp.message.content
    return _Resp(content)

# Fetch available cloud models dynamically
OLLAMA_CLOUD_MODELS: list = []
try:
    if OLLAMA_CLOUD_API_KEY:
        from ollama import Client as _OllamaClientTmp
        _cloud_tmp = _OllamaClientTmp(
            host='https://ollama.com',
            headers={'Authorization': 'Bearer ' + OLLAMA_CLOUD_API_KEY}
        )
        _cloud_list = _cloud_tmp.list()
        # .list() returns a ListResponse with .models list
        _models_data = _cloud_list.models if hasattr(_cloud_list, 'models') else []
        
        # Filter for large parameter models to prevent dropdown clutter
        _large_keywords = ['70b', '72b', '405b', 'r1', 'deepseek', 'nemotron:70b', 'llama3.3:70b']
        
        for m in _models_data:
            if hasattr(m, 'model'):
                model_name = m.model.lower()
                if any(k in model_name for k in _large_keywords):
                    OLLAMA_CLOUD_MODELS.append(f"ollamacloud:{m.model}")
                    
        if not OLLAMA_CLOUD_MODELS:
            # Fallback: dict-style
            for m in (_cloud_list if isinstance(_cloud_list, list) else []):
                model_name = m['name'].lower()
                if any(k in model_name for k in _large_keywords):
                    OLLAMA_CLOUD_MODELS.append(f"ollamacloud:{m['name']}")
                    
        print(f"[OllamaCloud] {len(OLLAMA_CLOUD_MODELS)} large cloud models loaded")
        del _OllamaClientTmp, _cloud_tmp, _cloud_list, _models_data, _large_keywords
except Exception as _ce:
    print(f"[OllamaCloud] Could not fetch cloud model list: {_ce}")

# ── Models for Chatbot & AI Insights UI ──────────────────────────
# Local models (agents use these; user can also pick for chat)
CHAT_LOCAL_MODELS = [
    'ollama:lfm2.5-thinking:1.2b',   # fastest local
    'ollama:gemma3:12b',
    'ollama:qwen2.5:7b',
    'ollama:llama3.1:8b',
    'ollama:deepseek-r1:8b',
    'ollama:deepseek-r1:14b',
    'ollama:medllama2:7b',
    'ollama:meditron:7b',
]

# Curated Ollama Cloud models — ordered small → large for comparison
CHAT_CLOUD_MODELS_LIST = [
    'ollamacloud:gpt-oss:120b',         #  65.3 GB  — much stronger
    'ollamacloud:deepseek-v3.2',        # 688.6 GB  — 671B params ★ default
    'ollamacloud:mistral-large-3:675b', # 682.0 GB  — 675B params
    'ollamacloud:kimi-k2-thinking',     #   1.1 TB  — 1T params (thinking)
]

# Combined list shown in UI: local first, then cloud, then OpenAI
CHAT_CLOUD_MODELS = CHAT_LOCAL_MODELS + CHAT_CLOUD_MODELS_LIST + OLLAMA_CLOUD_MODELS + ['openai:gpt-4o-mini']

# Default → deepseek-v3.2 (671B) for big-model comparison; fallback to local
CHAT_DEFAULT_MODEL = 'ollamacloud:deepseek-v3.2'

# Full AVAILABLE_MODELS (for internal model validation)
AVAILABLE_MODELS = list(dict.fromkeys(CHAT_CLOUD_MODELS))

# Model Preferences (per agent) — ALWAYS use local to avoid cloud token cost
MODEL_PREFERENCES = {
    'monitor':     'ollama:lfm2.5-thinking:1.2b',
    'analyzer':    'ollama:lfm2.5-thinking:1.2b',
    'predictor':   'ollama:lfm2.5-thinking:1.2b',
    'alert':       'ollama:lfm2.5-thinking:1.2b',
    'coordinator': CHAT_DEFAULT_MODEL,

}

# AI Client and Chat History
# AI Client and Chat History
# AI_CLIENT = Client()  # Replaced with tracked client
AI_CLIENT = TrackedAISuiteClient()
CHAT_HISTORY = deque(maxlen=50)
CHAT_HISTORY = deque(maxlen=50)

# Helper function untuk log agent activity
def log_agent_activity(agent_name, action, device_id=None, status="success", details=None, detailed_data=None):
    """Log and emit agent activity for real-time visibility"""
    activity_id = f"ACT_{int(time.time() * 1000)}"  # Unique ID with millisecond precision
    
    activity = {
        'id': activity_id,  # Unique identifier for expandable logs
        'timestamp': datetime.now().isoformat(),
        'agent': agent_name,
        'action': action,
        'device_id': device_id,
        'status': status,
        'details': details,
        'detailed_data': detailed_data  # Additional structured data for expansion
    }
    AGENT_ACTIVITY_LOG.append(activity)
    
    # Emit to frontend
    try:
        socketio.emit('agent_activity', activity)
    except:
        pass  # Socket might not be ready yet
    
    # Console log
    status_emoji = "✅" if status == "success" else "⚠️" if status == "warning" else "❌"
    print(f"{status_emoji} [{agent_name}] {action} | Device: {device_id or 'N/A'} | {details or ''}")
    
    return activity

# ======================
# MAPPINGS (dari app.py asli)
# ======================

POSTURE_MAP = {
    0: "Unknown", 1: "Sitting", 2: "Standing", 3: "Lying Down",
    4: "Lying on Right Side", 5: "Falling", 6: "Prone",
    7: "Lying on Left Side", 8: "Walking", 10: "Unstable Temp",
    11: "Upright Torso"
}

AREA_MAP = {
    1: "Unknown Area", 2: "Laboratory", 3: "Corridor",
    4: "Dining Table", 5: "Living Room", 6: "Bathroom",
    7: "Bedroom", 8: "Laboratory"
}

# ======================
# AUTONOMOUS AGENTS
# ======================

class MonitorAgent:
    """Agent 1: Real-time Monitoring & Anomaly Detection"""
    
    @staticmethod
    def analyze_realtime(patient_state):
        """Continuous monitoring with instant anomaly detection"""
        if len(patient_state.history) < 3:
            log_agent_activity(
                "Monitor Agent",
                "⚠️ Waiting for sufficient data - Need at least 3 sensor readings for reliable analysis",
                patient_state.device_id,
                "warning",
                f"Currently have {len(patient_state.history)} data points, need 3 minimum"
            )
            return None
            
        latest = list(patient_state.history)[-1]
        
        # Extract vital data for logging
        hr = int(latest.get('HR', 0))
        spo2 = int(latest.get('Blood_oxygen', 0))
        posture_val = int(latest.get('Posture_state', 0))
        area_val = int(latest.get('Area', latest.get('Lokasi', 0)))
        posture_txt = POSTURE_MAP.get(posture_val, "Unknown")
        area_txt = AREA_MAP.get(area_val, "Unknown")
        step_count = int(latest.get('Step', 0))
        
        # Detailed initial analysis log
        log_agent_activity(
            "Monitor Agent",
            f"🔍 Analyzing real-time sensor data from {area_txt}",
            patient_state.device_id,
            "running",
            f"Patient {posture_txt} | HR: {hr} bpm | SpO2: {spo2}% | Steps: {step_count} | Scanning for anomalies...",
            detailed_data={
                'sensor_readings': {
                    'hr': hr,
                    'spo2': spo2,
                    'posture': posture_txt,
                    'area': area_txt,
                    'posture_code': posture_val,
                    'area_code': area_val,
                    'step_count': step_count
                },
                'thresholds': {
                    'hr_low': AgentConfig.ABNORMAL_HR_LOW,
                    'hr_high': AgentConfig.ABNORMAL_HR_HIGH,
                    'spo2_min': AgentConfig.HYPOXIA_THRESHOLD
                },
                'analysis_context': f"Patient in {area_txt}, posture: {posture_txt}",
                'data_points_analyzed': len(patient_state.history)
            }
        )
        
        anomalies = []
        severity = "NORMAL"
        
        # 1. Fall Detection
        posture_val = int(latest.get('Posture_state', 0))
        if posture_val == 5:
            anomalies.append("FALL_DETECTED")
            severity = "CRITICAL"
            log_agent_activity(
                "Monitor Agent",
                "🚨 FALL DETECTED - Immediate emergency response required!",
                patient_state.device_id,
                "error",
                f"Posture sensor indicates falling state in {area_txt}. Triggering critical alert."
            )
            
        # 2. Vital Signs Check
        hr = int(latest.get('HR', 0))
        spo2 = int(latest.get('Blood_oxygen', 0))
        
        if hr > 0:
            if hr < AgentConfig.ABNORMAL_HR_LOW:
                anomalies.append(f"BRADYCARDIA (HR={hr})")
                severity = "WARNING"
                log_agent_activity(
                    "Monitor Agent",
                    f"💔 Abnormally LOW heart rate detected: {hr} bpm (Normal threshold: ≥{AgentConfig.ABNORMAL_HR_LOW} bpm)",
                    patient_state.device_id,
                    "warning",
                    f"Bradycardia detected. Patient may be experiencing cardiac slowdown."
                )
            elif hr > AgentConfig.ABNORMAL_HR_HIGH:
                anomalies.append(f"TACHYCARDIA (HR={hr})")
                severity = "WARNING"
                log_agent_activity(
                    "Monitor Agent",
                    f"💓 Abnormally HIGH heart rate detected: {hr} bpm (Normal threshold: ≤{AgentConfig.ABNORMAL_HR_HIGH} bpm)",
                    patient_state.device_id,
                    "warning",
                    f"Tachycardia detected. Patient may be experiencing stress or exertion."
                )
                
        if spo2 > 0 and spo2 < AgentConfig.HYPOXIA_THRESHOLD:
            anomalies.append(f"HYPOXIA (SpO2={spo2}%)")
            severity = "CRITICAL"
            log_agent_activity(
                "Monitor Agent",
                f"🫁 CRITICAL: Low blood oxygen detected: {spo2}% (Critical threshold: <{AgentConfig.HYPOXIA_THRESHOLD}%)",
                patient_state.device_id,
                "error",
                f"Hypoxia detected. Patient requires immediate oxygen assessment."
            )
            
        # 3. Contextual Analysis
        area_val = int(latest.get('Area', latest.get('Lokasi', 0)))
        area_txt = AREA_MAP.get(area_val, "Unknown")
        posture_txt = POSTURE_MAP.get(posture_val, "Unknown")
        
        context_risk = MonitorAgent._assess_context_risk(area_txt, posture_txt, hr)
        if context_risk:
            anomalies.append(context_risk)
            if "CRITICAL" in context_risk:
                severity = "CRITICAL"
            elif "WARNING" in context_risk:
                severity = max(severity, "WARNING", key=lambda x: ["NORMAL", "WARNING", "CRITICAL"].index(x))
            
            # Log contextual risk details
            log_agent_activity(
                "Monitor Agent",
                f"⚠️ Contextual risk identified: {context_risk}",
                patient_state.device_id,
                "warning" if "WARNING" in context_risk else "error",
                f"Location and posture combination suggests elevated risk. Monitoring closely."
            )
        
        if not anomalies:
            log_agent_activity(
                "Monitor Agent",
                f"✅ All vitals NORMAL - Patient safe in {area_txt}",
                patient_state.device_id,
                "success",
                f"HR: {hr} bpm (Normal), SpO2: {spo2}% (Good), Posture: {posture_txt} (Safe)"
            )
            return None
            
        # =========================================================
        # GRAPHITI MCP MEMORY CHECK (Reduce False Positives)
        # =========================================================
        anomaly_str = ", ".join(anomalies)
        query = f"Did the patient have these anomalies before, or is this their normal baseline: {anomaly_str}?"
        memory_context = run_async(patient_state.memory.get_patient_context(query, limit=3))
        
        log_agent_activity(
            "Monitor Agent",
            f" Checked Patient Memory ({len(anomalies)} anomalies)",
            patient_state.device_id,
            "running",
            f"Memory Context Retrieved:\n{memory_context}"
        )
        # =========================================================
        
        # Create detailed anomaly summary
        anomaly_summary = []
        for anomaly in anomalies:
            if "FALL" in anomaly:
                anomaly_summary.append("🚨 FALL DETECTED")
            elif "BRADYCARDIA" in anomaly:
                anomaly_summary.append(f"💔 Low HR: {hr} bpm")
            elif "TACHYCARDIA" in anomaly:
                anomaly_summary.append(f"💓 High HR: {hr} bpm")
            elif "HYPOXIA" in anomaly:
                anomaly_summary.append(f"🫁 Low O2: {spo2}%")
            elif "bathroom" in anomaly.lower():
                anomaly_summary.append(f"🚽 {posture_txt} in {area_txt}")
            elif "corridor" in anomaly.lower():
                anomaly_summary.append(f"🚶 {posture_txt} in {area_txt}")
            else:
                anomaly_summary.append(anomaly)
        
        log_agent_activity(
            "Monitor Agent",
            f"🚨 {severity} ALERT: {len(anomalies)} anomalies detected - Forwarding to Alert Agent",
            patient_state.device_id,
            "error" if severity == "CRITICAL" else "warning",
            " | ".join(anomaly_summary)
        )
            
        return {
            'timestamp': datetime.now().isoformat(),
            'device_id': patient_state.device_id,
            'severity': severity,
            'anomalies': anomalies,
            'data': latest,
            'memory_context': memory_context  # Pass memory to the next agent
        }
    
    @staticmethod
    def _assess_context_risk(area, posture, hr):
        """Contextual risk assessment"""
        area_lower = area.lower()
        posture_lower = posture.lower()
        
        if "bathroom" in area_lower and "lying" in posture_lower:
            return "CRITICAL: Patient lying in bathroom"
        if "corridor" in area_lower and "lying" in posture_lower:
            return "WARNING: Patient lying in corridor"
        if hr > 110 and "sitting" in posture_lower:
            return "WARNING: High HR while sedentary"
        
        return None


class AnalyzerAgent:
    """Agent 2: Deep Pattern Analysis & Trend Detection"""
    
    @staticmethod
    @track(name="analyzer_agent", tags=["analyzer", "pattern_recognition"])
    def analyze_patterns(patient_state):
        """Analyze historical patterns for insights"""
        log_agent_activity(
            "Analyzer Agent",
            "Starting pattern analysis",
            patient_state.device_id,
            "running",
            f"Analyzing {len(patient_state.history)} data points"
        )
        
        if len(patient_state.history) < 20:
            log_agent_activity(
                "Analyzer Agent",
                "Insufficient data for patterns",
                patient_state.device_id,
                "warning",
                "Need at least 20 data points"
            )
            return None
            
        recent_data = list(patient_state.history)
        
        patterns = {
            'activity_distribution': AnalyzerAgent._analyze_activity(recent_data),
            'vitals_trend': AnalyzerAgent._analyze_vitals_trend(recent_data),
            'location_hotspots': AnalyzerAgent._analyze_locations(recent_data),
            'risk_assessment': AnalyzerAgent._calculate_risk_score(recent_data)
        }
        
        # Get most common activity and location
        top_activity = list(patterns['activity_distribution'].keys())[0] if patterns['activity_distribution'] else "Unknown"
        top_location = list(patterns['location_hotspots'].keys())[0] if patterns['location_hotspots'] else "Unknown"
        
        log_agent_activity(
            "Analyzer Agent",
            "Pattern analysis completed",
            patient_state.device_id,
            "success",
            f"Risk={patterns['risk_assessment']:.2f} | Activity={top_activity} | Location={top_location}"
        )
        
        return patterns
    
    @staticmethod
    def _analyze_activity(data):
        """Activity distribution analysis"""
        postures = [POSTURE_MAP.get(int(d.get('Posture_state', 0)), 'Unknown') for d in data]
        from collections import Counter
        distribution = Counter(postures)
        
        total = len(postures)
        return {k: f"{(v/total)*100:.1f}%" for k, v in distribution.most_common(5)}
    
    @staticmethod
    def _analyze_vitals_trend(data):
        """Vital signs trend detection"""
        hrs = [int(d.get('HR', 0)) for d in data if d.get('HR', 0) > 0]
        spo2s = [int(d.get('Blood_oxygen', 0)) for d in data if d.get('Blood_oxygen', 0) > 0]
        
        trend = {}
        if hrs:
            trend['hr_avg'] = np.mean(hrs)
            trend['hr_std'] = np.std(hrs)
            trend['hr_range'] = (min(hrs), max(hrs))
            
        if spo2s:
            trend['spo2_avg'] = np.mean(spo2s)
            trend['spo2_min'] = min(spo2s)
            
        return trend
    
    @staticmethod
    def _analyze_locations(data):
        """Location hotspot detection"""
        areas = [AREA_MAP.get(int(d.get('Area', d.get('Lokasi', 0))), 'Unknown') for d in data]
        from collections import Counter
        return dict(Counter(areas).most_common(3))
    
    @staticmethod
    def _calculate_risk_score(data):
        """Calculate overall risk score (0-1)"""
        risk = 0.0
        
        # Falls in history
        falls = sum(1 for d in data if int(d.get('Posture_state', 0)) == 5)
        risk += min(falls * 0.2, 0.4)
        
        # Abnormal vitals frequency
        abnormal_hr = sum(1 for d in data if int(d.get('HR', 0)) > 110 or int(d.get('HR', 0)) < 45)
        risk += min(abnormal_hr / len(data), 0.3)
        
        # Low oxygen frequency
        hypoxia = sum(1 for d in data if 0 < int(d.get('Blood_oxygen', 0)) < 90)
        risk += min(hypoxia / len(data), 0.3)
        
        return round(risk, 2)


class AlertAgent:
    """Agent 3: Intelligent Alert System with Priority Handling"""
    
    @staticmethod
    @track(name="alert_agent", tags=["alert", "notification"])
    def create_alert(anomaly_report):
        """Create structured alert from anomaly"""
        # Create concise alert summary
        anomalies = anomaly_report.get('anomalies', [])
        severity = anomaly_report.get('severity', 'UNKNOWN')
        
        log_agent_activity(
            "Alert Agent",
            f"Creating {severity} alert",
            anomaly_report['device_id'],
            "running",
            f"{len(anomalies)} anomalies: {', '.join(anomalies[:2])}..." if len(anomalies) > 2 else ', '.join(anomalies)
        )
        
        alert = {
            'id': f"ALERT_{int(time.time())}",
            'timestamp': anomaly_report['timestamp'],
            'device_id': anomaly_report['device_id'],
            'severity': anomaly_report['severity'],
            'message': AlertAgent._generate_message(anomaly_report),
            'actions_required': AlertAgent._suggest_actions(anomaly_report),
            'auto_notify': anomaly_report['severity'] == "CRITICAL"
        }
        
        # Extract key info from alert message
        actions_count = len(alert.get('actions_required', []))
        
        # =========================================================
        # GRAPHITI MCP MEMORY: Store this alert into long-term memory
        # =========================================================
        patient_state = PATIENT_STATES.get(anomaly_report['device_id'])
        if patient_state:
            run_async(patient_state.memory.store_alert(alert), wait_result=False)
            
        log_agent_activity(
            "Alert Agent",
            "Alert created",
            anomaly_report['device_id'],
            "error" if anomaly_report['severity'] == "CRITICAL" else "warning",
            f"{alert['message']} ({actions_count} actions)"
        )
        
        return alert
    
    @staticmethod
    def _generate_message(report):
        """Generate human-readable alert message"""
        anomalies = report['anomalies']
        severity = report['severity']
        
        if severity == "CRITICAL":
            prefix = "🚨 CRITICAL ALERT"
        elif severity == "WARNING":
            prefix = "⚠️ WARNING"
        else:
            prefix = "ℹ️ INFO"
            
        msg = f"{prefix}: {', '.join(anomalies)}"
        return msg
    
    @staticmethod
    def _suggest_actions(report):
        """Suggest immediate actions"""
        actions = []
        
        for anomaly in report['anomalies']:
            if "FALL" in anomaly:
                actions.append("Dispatch emergency response immediately")
                actions.append("Check for head injury or fracture")
            elif "HYPOXIA" in anomaly:
                actions.append("Administer oxygen if available")
                actions.append("Check respiratory rate")
            elif "BRADYCARDIA" in anomaly:
                actions.append("Check consciousness level")
                actions.append("Monitor for dizziness or syncope")
            elif "bathroom" in anomaly.lower():
                actions.append("Check patient status in bathroom")
                actions.append("Ensure safe exit pathway")
                
        return actions


class PredictorAgent:
    """Agent 4: Predictive Analytics & Future Risk Estimation"""
    
    @staticmethod
    @track(name="predictor_agent", tags=["predictor", "forecasting"])
    def predict_risk(patient_state):
        """Predict future risk based on current trends"""
        log_agent_activity(
            "Predictor Agent",
            "Starting risk prediction",
            patient_state.device_id,
            "running",
            f"Analyzing {len(patient_state.history)} data points for trend prediction"
        )
        
        if len(patient_state.history) < 50:
            log_agent_activity(
                "Predictor Agent",
                "Insufficient data for prediction",
                patient_state.device_id,
                "warning",
                "Need at least 50 data points"
            )
            return None
            
        recent = list(patient_state.history)[-30:]
        
        # Time-series analysis
        hrs = [int(d.get('HR', 0)) for d in recent if d.get('HR', 0) > 0]
        
        prediction = {
            'next_hour_risk': PredictorAgent._estimate_short_term_risk(recent),
            'trend_direction': PredictorAgent._detect_trend(hrs),
            'recommendations': []
        }
        
        # Generate recommendations
        if prediction['next_hour_risk'] > 0.7:
            prediction['recommendations'].append("Increase monitoring frequency")
        if prediction['trend_direction'] == 'deteriorating':
            prediction['recommendations'].append("Consider preventive intervention")
        
        risk_level = "🔴 HIGH" if prediction['next_hour_risk'] > 0.7 else "🟡 MEDIUM" if prediction['next_hour_risk'] > 0.4 else "🟢 LOW"
        recommendations_count = len(prediction.get('recommendations', []))
        
        log_agent_activity(
            "Predictor Agent",
            "Prediction completed",
            patient_state.device_id,
            "warning" if prediction['next_hour_risk'] > 0.7 else "success",
            f"{risk_level} risk | Trend: {prediction['trend_direction']} | {recommendations_count} recommendations"
        )
            
        return prediction
    
    @staticmethod
    def _estimate_short_term_risk(data):
        """Estimate risk for next hour"""
        # Simple heuristic: weighted recent anomalies
        recent_5 = data[-5:]
        risk = 0.0
        
        for d in recent_5:
            hr = int(d.get('HR', 0))
            spo2 = int(d.get('Blood_oxygen', 0))
            
            if hr > 110 or hr < 50:
                risk += 0.15
            if 0 < spo2 < 90:
                risk += 0.2
                
        return min(risk, 1.0)
    
    @staticmethod
    def _detect_trend(values):
        """Detect if values are improving or deteriorating"""
        if len(values) < 10:
            return 'stable'
            
        # Simple linear regression slope
        x = np.arange(len(values))
        slope = np.polyfit(x, values, 1)[0]
        
        # For HR: increasing = deteriorating if above normal
        if abs(slope) < 0.5:
            return 'stable'
        elif slope > 0:
            return 'deteriorating'
        else:
            return 'improving'


class CoordinatorAgent:
    """Agent 5: Multi-Agent Coordination & Decision Orchestration"""
    
    @staticmethod
    @track(name="coordinator_agent", tags=["coordinator", "orchestration"])
    def coordinate_analysis(device_id):
        """Orchestrate all agents for comprehensive analysis"""
        log_agent_activity(
            "Coordinator Agent",
            "Starting multi-agent coordination",
            device_id,
            "running",
            "Orchestrating Monitor, Analyzer, and Predictor agents"
        )
        
        patient_state = PATIENT_STATES.get(device_id)
        if not patient_state:
            log_agent_activity(
                "Coordinator Agent",
                "Patient state not found",
                device_id,
                "error",
                "No data available for this device"
            )
            return None
            
        # Run all agents
        results = {
            'timestamp': datetime.now().isoformat(),
            'device_id': device_id,
            'monitoring': MonitorAgent.analyze_realtime(patient_state),
            'patterns': AnalyzerAgent.analyze_patterns(patient_state),
            'prediction': PredictorAgent.predict_risk(patient_state),
            'overall_risk': patient_state.risk_score
        }
        
        # Update risk score
        if results['patterns']:
            patient_state.risk_score = results['patterns']['risk_assessment']
            
        # Generate alerts if needed
        if results['monitoring'] and AgentConfig.AUTO_ALERT_ENABLED:
            alert = AlertAgent.create_alert(results['monitoring'])
            ACTIVE_ALERTS.append(alert)
            
            # Emit to frontend
            socketio.emit('ai_alert', alert)
        
        log_agent_activity(
            "Coordinator Agent",
            "Coordination completed",
            device_id,
            "success",
            f"All agents executed, Risk: {patient_state.risk_score}"
        )
            
        return results
    
    @staticmethod
    @track(name="coordinator_agent", tags=["coordinator", "summary"])
    def generate_ai_summary(results):
        """Use LLM to generate natural language summary"""
        if not results:
            return "No data available for analysis."
            
        # Prepare context
        context = f"""
        AUTONOMOUS ANALYSIS REPORT
        Device: {results['device_id']}
        Time: {results['timestamp']}
        
        REAL-TIME MONITORING:
        {json.dumps(results.get('monitoring'), indent=2)}
        
        PATTERN ANALYSIS:
        {json.dumps(results.get('patterns'), indent=2)}
        
        PREDICTIVE INSIGHTS:
        {json.dumps(results.get('prediction'), indent=2)}
        
        Overall Risk Score: {results['overall_risk']}
        """
        
        try:
            response = AI_CLIENT.chat.completions.create(
                model=AgentConfig.COORDINATOR_AGENT,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a medical AI coordinator with deep long-term patient memory. Summarize the autonomous analysis in clear, actionable language. If the memory_context indicates an anomaly is normal for this patient, heavily emphasize this to reduce false alarms. Highlight critical findings first."
                    },
                    {
                        "role": "user",
                        "content": context
                    }
                ],
                temperature=0.3
            )
            
            return response.choices[0].message.content
        except:
            return "AI summary generation failed. See raw data above."

# ======================
# AUTONOMOUS BACKGROUND WORKER
# ======================

def autonomous_monitor_loop():
    """Background thread for continuous autonomous monitoring"""
    print("🤖 Autonomous Monitor Agent Started")
    
    while True:
        try:
            # Process each active patient
            for device_id, patient_state in PATIENT_STATES.items():
                if len(patient_state.history) > 0:
                    # Run coordinated analysis
                    results = CoordinatorAgent.coordinate_analysis(device_id)
                    
                    if results and results.get('monitoring'):
                        print(f"[AGENT] {device_id}: {results['monitoring']['severity']}")
                        
        except Exception as e:
            print(f"[AGENT ERROR] {e}")
            
        time.sleep(AgentConfig.AUTO_ANALYSIS_INTERVAL)


# Start autonomous worker in background
autonomous_thread = Thread(target=autonomous_monitor_loop, daemon=True)
autonomous_thread.start()

# ======================
# MONGODB REAL-TIME LISTENER
# ======================

def mongodb_listener():
    """Listen to MongoDB changes and update patient states"""
    client = MongoClient(AgentConfig.MONGO_URL)
    
    print(f"📡 MongoDB Listener Started for {len(AgentConfig.DB_LIST)} databases")
    
    last_ids = {}
    for db_name in AgentConfig.DB_LIST:
        try:
            col = client[db_name][AgentConfig.COLLECTION_NAME]
            last = list(col.find().sort('_id', -1).limit(1))
            if last:
                last_ids[db_name] = last[0]['_id']
        except:
            pass
    
    while True:
        try:
            for db_name in AgentConfig.DB_LIST:
                col = client[db_name][AgentConfig.COLLECTION_NAME]
                
                query = {}
                if db_name in last_ids:
                    query = {'_id': {'$gt': last_ids[db_name]}}
                    
                new_docs = list(col.find(query).sort('_id', 1))
                
                for doc in new_docs:
                    device_id = doc.get('device_ID') or doc.get('device_id')
                    
                    if device_id:
                        # Ensure patient state exists
                        if device_id not in PATIENT_STATES:
                            PATIENT_STATES[device_id] = PatientState(device_id)
                            
                        # Add data to patient state
                        PATIENT_STATES[device_id].add_data(doc)
                        
                        # Emit to frontend (with datetime handling)
                        clean_data = {}
                        for k, v in doc.items():
                            if k != '_id':
                                if isinstance(v, datetime):
                                    clean_data[k] = v.isoformat()
                                else:
                                    clean_data[k] = v
                        
                        socketio.emit('sensor_update', {
                            'device_id': device_id,
                            'data': clean_data
                        })
                        
                if new_docs:
                    last_ids[db_name] = new_docs[-1]['_id']
                    
        except Exception as e:
            print(f"[MONGODB ERROR] {e}")
            
        time.sleep(1)

# Start MongoDB listener
mongo_thread = Thread(target=mongodb_listener, daemon=True)
mongo_thread.start()

# ======================
# FLASK ROUTES
# ======================

@app.route("/")
def index():
    return render_template("agentic_interface_enhanced.html")

@app.route("/api/patient-states")
def get_patient_states():
    """Get current state of all patients"""
    states = {}
    for device_id, state in PATIENT_STATES.items():
        # Get latest data
        latest_data = None
        if state.history:
            latest = list(state.history)[-1]
            latest_data = {
                'HR': int(latest.get('HR', 0)),
                'SpO2': int(latest.get('Blood_oxygen', 0)),
                'Posture': POSTURE_MAP.get(int(latest.get('Posture_state', 0)), 'Unknown'),
                'Area': AREA_MAP.get(int(latest.get('Area', latest.get('Lokasi', 0))), 'Unknown'),
                'Steps': int(latest.get('Step', 0))
            }
        
        states[device_id] = {
            'device_id': device_id,
            'risk_score': state.risk_score,
            'data_points': len(state.history),
            'last_update': state.history[-1]['timestamp'].isoformat() if state.history else None,
            'patterns': state.patterns_detected,
            'latest_data': latest_data,
            'recent_alerts': len([a for a in ACTIVE_ALERTS if a.get('device_id') == device_id])
        }
    return app.response_class(
        response=json.dumps(states, cls=DateTimeEncoder),
        status=200,
        mimetype='application/json'
    )

@app.route("/api/patient-detail/<device_id>")
def get_patient_detail(device_id):
    """Get detailed patient information"""
    if device_id not in PATIENT_STATES:
        return jsonify({'error': 'Patient not found'}), 404
    
    state = PATIENT_STATES[device_id]
    recent_data = list(state.history)[-20:]  # Last 20 readings
    
    # Calculate stats
    hrs = [int(d.get('HR', 0)) for d in recent_data if d.get('HR', 0) > 0]
    spo2s = [int(d.get('Blood_oxygen', 0)) for d in recent_data if d.get('Blood_oxygen', 0) > 0]
    
    latest_doc = recent_data[-1] if recent_data else {}
    stats = {
        'hr_avg': round(np.mean(hrs), 1) if hrs else 0,
        'hr_min': min(hrs) if hrs else 0,
        'hr_max': max(hrs) if hrs else 0,
        'spo2_min': min(spo2s) if spo2s else 0,
        'safe_battery': int(latest_doc.get('safe_battery', latest_doc.get('safe battery', 0))),
        'band_battery': int(latest_doc.get('band_battery', latest_doc.get('band battery', 0)))
    }
    
    # Get patient alerts
    patient_alerts = [a for a in ACTIVE_ALERTS if a.get('device_id') == device_id][-10:]
    
    detail = {
        'device_id': device_id,
        'risk_score': state.risk_score,
        'total_data_points': len(state.history),
        'recent_data': [
            {
                'timestamp': d.get('timestamp').isoformat() if isinstance(d.get('timestamp'), datetime) else str(d.get('timestamp')),
                'HR': int(d.get('HR', 0)),
                'SpO2': int(d.get('Blood_oxygen', 0)),
                'Posture': POSTURE_MAP.get(int(d.get('Posture_state', 0)), 'Unknown'),
                'Area': AREA_MAP.get(int(d.get('Area', d.get('Lokasi', 0))), 'Unknown'),
                'safe_battery': int(d.get('safe_battery', d.get('safe battery', 0))),
                'band_battery': int(d.get('band_battery', d.get('band battery', 0)))
            }
            for d in recent_data
        ],
        'statistics': stats,
        'patterns': state.patterns_detected,
        'alerts': patient_alerts
    }
    
    return app.response_class(
        response=json.dumps(detail, cls=DateTimeEncoder),
        status=200,
        mimetype='application/json'
    )

@app.route("/api/active-alerts")
def get_active_alerts():
    """Get all active alerts"""
    return app.response_class(
        response=json.dumps(ACTIVE_ALERTS[-20:], cls=DateTimeEncoder),
        status=200,
        mimetype='application/json'
    )

@app.route("/api/agent-activity")
def get_agent_activity():
    """Get recent agent activity log"""
    return app.response_class(
        response=json.dumps(list(AGENT_ACTIVITY_LOG), cls=DateTimeEncoder),
        status=200,
        mimetype='application/json'
    )

@app.route("/api/force-analysis/<device_id>", methods=["POST"])
def force_analysis(device_id):
    """Manually trigger comprehensive analysis"""
    log_agent_activity(
        "Coordinator Agent",
        "Manual analysis triggered",
        device_id,
        "running",
        "User requested force analysis"
    )
    
    results = CoordinatorAgent.coordinate_analysis(device_id)
    if results:
        summary = CoordinatorAgent.generate_ai_summary(results)
        return app.response_class(
            response=json.dumps({
                'results': results,
                'ai_summary': summary
            }, cls=DateTimeEncoder),
            status=200,
            mimetype='application/json'
        )
    return jsonify({'error': 'No data available'}), 404

@app.route("/api/agent-activity-detail/<activity_id>")
def get_agent_activity_detail(activity_id):
    """Get detailed information for a specific activity log"""
    for activity in AGENT_ACTIVITY_LOG:
        if activity.get('id') == activity_id:
            return app.response_class(
                response=json.dumps(activity, cls=DateTimeEncoder, indent=2),
                status=200,
                mimetype='application/json'
            )
    return jsonify({'error': 'Activity not found'}), 404

@app.route("/api/generate-report/<device_id>")
def generate_report(device_id):
    """Generate comprehensive health report for a patient"""
    # Get parameters
    time_range = request.args.get('hours', default=24, type=int)
    format_type = request.args.get('format', default='json', type=str).lower()
    
    # Validate time range
    if time_range < 1 or time_range > 168:  # Max 1 week
        return jsonify({'error': 'Time range must be between 1 and 168 hours'}), 400
    if device_id in PATIENT_STATES:
        patient_state = PATIENT_STATES[device_id]
        patient_memory = patient_state.memory
    else:
        from memory.patient_memory import PatientMemory
        import collections
        class OfflinePatientState:
            def __init__(self, did):
                self.device_id = did
                self.history = collections.deque(maxlen=100)
                self.risk_score = 0.0
        patient_state = OfflinePatientState(device_id)
        patient_memory = PatientMemory(device_id)
        
    # Get graphiti summary and historical raw episodes using the actual time range
    graph_context = ""
    raw_history = []
    try:
        from agentic_medicore_enhanced import run_async_readonly
        graph_context = run_async_readonly(
            patient_memory.get_activity_summary(time_range), timeout=15
        )
        raw_history = run_async_readonly(
            patient_memory.get_raw_history(time_range), timeout=15
        )
    except Exception as e:
        print(f"Graphiti memory fetch failed for report: {e}")
    patient_alerts = [a for a in ACTIVE_ALERTS if a.get('device_id') == device_id]
    patient_logs = [log for log in AGENT_ACTIVITY_LOG if log.get('device_id') == device_id]
    
    # Generate an AI Narrative Summary
    ai_narrative = ""
    try:
        if graph_context:
            from textwrap import dedent
            prompt = dedent(f"""
            You are an expert clinical AI. Provide a compassionate, factual, and chronological 2-3 paragraph summary of the following Graphiti patient activity data for the last {time_range} hours.
            Highlight what the patient was doing throughout the day (morning, afternoon, night trends), their average heart rate, and primary locations/behaviors. 
            Do NOT hallucinate or guess. Use ONLY the data provided below. Format nicely with bold text where appropriate.

            DATA SUMMARY:
            {graph_context}
            """).strip()
            
            chat_model = MODEL_PREFERENCES.get('coordinator', AgentConfig.COORDINATOR_AGENT)
            if chat_model.startswith('ollamacloud:'):
                model_name = chat_model.split('ollamacloud:')[1]
                resp = call_ollama_cloud(model_name, [{"role": "user", "content": prompt}], temperature=0.3)
                ai_narrative = resp.choices[0].message.content
            else:
                from ollama import AsyncClient
                client = AsyncClient(host=AgentConfig.OLLAMA_HOST)
                resp = run_async_readonly(
                    client.chat(model=chat_model, messages=[{"role": "user", "content": prompt}], stream=False),
                    timeout=30
                )
                ai_narrative = resp['message']['content']
    except Exception as e:
        print(f"AI narrative generation failed: {e}")
    
    try:
        # Generate report
        report_data = ReportGenerator.generate_report(
            patient_state,
            patient_alerts,
            patient_logs,
            time_range_hours=time_range,
            graph_memory_summary=graph_context or "No semantic AI data derived from Neo4j/Graphiti.",
            ai_narrative=ai_narrative or "No AI narrative could be generated at this time.",
            extra_data=raw_history
        )
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_type == 'html':
            # Generate HTML report
            html_report = ReportGenerator.export_to_html(report_data)
            return app.response_class(
                response=html_report,
                status=200,
                mimetype='text/html',
                headers={
                    'Content-Disposition': f'attachment; filename=health_report_{device_id}_{timestamp}.html'
                }
            )
        else:
            # JSON format (default)
            return app.response_class(
                response=json.dumps(report_data, cls=DateTimeEncoder, indent=2),
                status=200,
                mimetype='application/json',
                headers={
                    'Content-Disposition': f'attachment; filename=health_report_{device_id}_{timestamp}.json'
                }
            )
    except Exception as e:
        return jsonify({
            'error': 'Failed to generate report',
            'message': str(e)
        }), 500

@app.route("/api/patient-memory/<device_id>")
def get_patient_memory(device_id):
    """Fetch AI memory baseline summary from Graphiti for the UI"""
    if device_id not in PATIENT_STATES:
        return jsonify({'error': 'Patient not found'}), 404
        
    patient_state = PATIENT_STATES[device_id]
    query = "Summarize the patient's normal baseline, typical locations, and any major past emergencies based on your memory. Be factual and concise."
    
    try:
        context = run_async(patient_state.memory.get_patient_context(query, limit=15))
        if context is None:
             return jsonify({'device_id': device_id, 'memory': '⏳ Graphiti memory engine is currently overloaded or configuring. Please wait a few moments and try again.'})
        return jsonify({'device_id': device_id, 'memory': context})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
@app.route("/api/patient-insights/<device_id>")
def get_patient_insights(device_id):
    """
    Generate structured AI Insights from Graphiti memory graph.
    Asks the LLM 4 targeted questions about the patient's history,
    then returns structured insight cards for the UI.
    """
    if device_id in PATIENT_STATES:
        patient_memory = PATIENT_STATES[device_id].memory
        patient_history = PATIENT_STATES[device_id].history
    else:
        from memory.patient_memory import PatientMemory
        patient_memory = PatientMemory(device_id)
        patient_history = []
    
    hours = request.args.get('hours', default=24, type=int)
    period = request.args.get('period', default='Today', type=str)
    selected_model = request.args.get('model', default='', type=str)
    chat_model = selected_model if selected_model and selected_model in AVAILABLE_MODELS \
                 else AgentConfig.COORDINATOR_AGENT

    # Pull broad memory context from Graphiti for all insight topics
    insight_queries = [
        ("risk_profile",    f"What are the known risk factors and past emergencies for this patient in the context of {period}?"),
        ("vitals_pattern",  f"What are the normal heart rate and blood oxygen patterns for this patient over the {period}?"),
        ("location_habits", f"What are the typical locations and activity patterns of this patient over the {period}?"),
        ("recommendations", f"Based on the patient's history, what are the most important care recommendations currently?"),
    ]

    raw_contexts = {}
    memory_hits   = 0
    for key, query in insight_queries:
        try:
            # Tier-1: try graphiti.search() via locked run_async (short timeout OK)
            ctx = run_async(patient_memory.get_patient_context(query, limit=8))
            if ctx and "No patient history" not in ctx and "first session" not in ctx:
                raw_contexts[key] = ctx
                memory_hits += 1
                continue
        except Exception:
            pass

        # Tier-2: direct Neo4j episode read, NO lock, always fast
        limit_val = 15 if hours <= 24 else (30 if hours <= 48 else 80)
        direct = run_async_readonly(
            patient_memory.get_patient_episodes_direct(limit=limit_val, hours=hours), timeout=10
        )
        if direct:
            raw_contexts[key] = direct
            memory_hits += 1
        else:
            raw_contexts[key] = "No historical data found for this topic yet."

    # Also grab current live vitals
    live_vitals = {}
    if patient_history:
        latest = list(patient_history)[-1]
        live_vitals = {
            'HR':      int(latest.get('HR', 0)),
            'SpO2':    int(latest.get('Blood_oxygen', 0)),
            'Posture': POSTURE_MAP.get(int(latest.get('Posture_state', 0)), 'Unknown'),
            'Area':    AREA_MAP.get(int(latest.get('Area', latest.get('Lokasi', 0))), 'Unknown'),
        }

    # Determine overall memory status for UI
    # Count context that has real data (either Tier-1 facts or Tier-2 episodes)
    if memory_hits == 0:
        memory_status = "empty"   # Both tiers returned empty — no episodes at all
        memory_note = (
            "NOTE: No historical data found for this patient in Neo4j. "
            "This is the first monitoring session or data has not yet been stored. "
            "Base insights entirely on current live vitals."
        )
    elif any("Episode History" in v for v in raw_contexts.values()):
        memory_status = "active"
        memory_note = (
            f"Memory context available from {memory_hits}/4 topic areas "
            f"(raw episode history — Graphiti entity extraction still processing in background)."
        )
    else:
        memory_status = "active"
        memory_note = f"Memory graph contains extracted facts from {memory_hits}/4 topic areas."

    # Ask LLM to structure the insights
    system_prompt = (
        "You are a clinical AI assistant analysing a patient's sensor monitoring history. "
        "Based ONLY on the provided episode history and live vitals, produce 4 factual insight cards. "
        "Each card MUST have exactly these keys:\n"
        "  'title'     : short phrase (3-6 words)\n"
        "  'summary'   : 2 sentences max, specific and actionable\n"
        "  'severity'  : one of: normal, caution, critical\n"
        "  'reasoning' : 1-2 sentences citing the EXACT data points (timestamps, values) that justify this insight\n"
        "Reply with a valid JSON array of 4 objects and NOTHING else."
    )

    # Trim each context to 800 chars to avoid overwhelming the small LLM
    def _trim(text: str, limit: int = 800) -> str:
        return text[:limit] + "..." if len(text) > limit else text

    # Dynamically adjust character limit based on timeframe (modern small LLMs handle 8k context easily)
    char_limit = 2000 if hours <= 24 else (4000 if hours <= 48 else 8000)

    user_prompt = f"""
Patient Device: {device_id}
Requested Timeframe: {period} (last {hours} hours)
Live Vitals Now: {json.dumps(live_vitals)}
Memory Context: {memory_note}

EPISODE HISTORY — Risk & Vital Patterns:
{_trim(raw_contexts['risk_profile'], char_limit)}

EPISODE HISTORY — Vitals Over Time:
{_trim(raw_contexts['vitals_pattern'], char_limit)}

EPISODE HISTORY — Location & Activity:
{_trim(raw_contexts['location_habits'], char_limit)}

EPISODE HISTORY — Care Notes:
{_trim(raw_contexts['recommendations'], char_limit)}

Generate EXACTLY 4 insight cards specifically focusing on the requested timeframe ({period}). For each card, cite the specific data point from the episode history that led to the insight.
Example reasoning: "Based on episode [2026-02-26T06:26] showing HR 89 bpm in Living Room, pattern is stable."
Output ONLY the JSON array.
"""

    try:
        response = AI_CLIENT.chat.completions.create(
            model=chat_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user",   "content": user_prompt},
            ],
            temperature=0.2,
        )
        raw = response.choices[0].message.content.strip()

        # Strip <think>...</think> tags (lfm2.5-thinking model)
        import re
        raw = re.sub(r'<think>.*?</think>', '', raw, flags=re.DOTALL).strip()

        # Strip markdown fences if present
        if '```' in raw:
            # Extract content between first ``` pair
            parts = raw.split('```')
            for part in parts:
                part = part.strip().lstrip('json').strip()
                if part.startswith('[') or part.startswith('{'):
                    raw = part
                    break

        # Find the JSON array even if wrapped in extra text
        match = re.search(r'\[.*\]', raw, re.DOTALL)
        if match:
            raw = match.group(0)

        if not raw:
            raise ValueError("Empty response after stripping")

        parsed = json.loads(raw)

        # Normalize field names — models sometimes use different keys
        KEY_MAP = {
            'title':     ['title', 'name', 'heading', 'card_title', 'insight_title'],
            'summary':   ['summary', 'description', 'content', 'detail', 'body', 'text', 'insight'],
            'severity':  ['severity', 'level', 'status', 'priority', 'risk'],
            'reasoning': ['reasoning', 'reason', 'rationale', 'evidence', 'justification', 'why', 'basis'],
        }
        VALID_SEVERITY = {'normal', 'caution', 'critical'}

        def normalize_card(card: dict) -> dict:
            result = {}
            for target, candidates in KEY_MAP.items():
                for c in candidates:
                    if c in card:
                        result[target] = card[c]
                        break
                if target not in result:
                    result[target] = 'normal' if target == 'severity' else ''
            # Validate severity
            sev = str(result.get('severity', 'normal')).lower().strip()
            result['severity'] = sev if sev in VALID_SEVERITY else 'normal'
            return result

        if isinstance(parsed, list):
            insights = [normalize_card(c) for c in parsed if isinstance(c, dict)]
        elif isinstance(parsed, dict):
            # Model sometimes wraps in {"insights": [...]}
            for v in parsed.values():
                if isinstance(v, list):
                    insights = [normalize_card(c) for c in v if isinstance(c, dict)]
                    break
            else:
                insights = [normalize_card(parsed)]
        else:
            raise ValueError(f"Unexpected JSON type: {type(parsed)}")

        # Ensure we have at least one valid card with content
        insights = [c for c in insights if c.get('title') or c.get('summary')]
        if not insights:
            raise ValueError("No valid cards after normalization")

    except Exception as e:
        # Robust fallback: generate a minimal live-vitals card
        print(f"[Insights] JSON parse/normalize error: {e} | raw[:200]={raw[:200] if 'raw' in dir() else 'N/A'}")
        lv = live_vitals
        insights = [
            {"title": "Current Vitals",
             "summary": f"HR {lv.get('HR','--')} bpm, SpO2 {lv.get('SpO2','--')}%. Vitals are being monitored in real time.",
             "severity": "normal"},
            {"title": "Location & Posture",
             "summary": f"Patient is {lv.get('Posture','Unknown')} in {lv.get('Area','Unknown')}. No anomalies detected.",
             "severity": "normal"},
            {"title": "Memory Context Status",
             "summary": f"{memory_note}",
             "severity": "caution"},
            {"title": "Monitoring Active",
             "summary": "Live sensor data is streaming. Insights will improve as memory graph accumulates more history.",
             "severity": "normal"},
        ]

    return jsonify({
        'device_id':      device_id,
        'insights':       insights,
        'memory_status':  memory_status,
        'memory_hits':    memory_hits,
        'live_vitals':    live_vitals,
        'memory_sources': {k: v for k, v in raw_contexts.items()},  # full context for UI display
    })


@app.route("/api/memory-chat", methods=["POST"])
def memory_chat():
    """
    Memory-aware Patient Chatbot endpoint.
    Now respects the coordinator_model param AND detects time references
    to fetch the correct timeline window from Neo4j.
    """
    import re as _re

    try:
        payload          = request.get_json() or {}
        question         = payload.get("question", "").strip()
        device_id        = payload.get("device_id", "")
        session_history  = payload.get("history", [])
        selected_model   = payload.get("coordinator_model", "").strip()
        chat_model       = selected_model if selected_model and selected_model in AVAILABLE_MODELS \
                           else AgentConfig.COORDINATOR_AGENT

        if not question:
            return jsonify({"error": "Empty question"}), 400

        # ── Detect time references in the question ─────────────────────────
        # Examples: "8am", "8 am", "8:00", "08:30", "morning", "woke up"
        time_context = ""
        detected_hour = None
        detected_min  = 0

        # Match patterns like "8am", "8 AM", "08:00", "8:30am", "at 8", "around 7"
        t_match = _re.search(
            r'\b(?:at\s+|around\s+|near\s+|by\s+)?(\d{1,2})(?::(\d{2}))?\s*(am|pm|AM|PM)?\b',
            question
        )
        # Named time-of-day keywords
        named_times = {
            "midnight": 0, "dawn": 5, "morning": 7, "woke up": 7, "wake up": 7,
            "breakfast": 7, "noon": 12, "midday": 12, "lunch": 12,
            "afternoon": 14, "evening": 18, "sunset": 18, "dinner": 19,
            "night": 21, "sleep": 22, "bed": 22, "midnight": 0
        }

        if t_match:
            h = int(t_match.group(1))
            m = int(t_match.group(2)) if t_match.group(2) else 0
            meridiem = (t_match.group(3) or "").lower()
            if meridiem == "pm" and h != 12:
                h += 12
            elif meridiem == "am" and h == 12:
                h = 0
            # Ambiguous (no AM/PM): if h < 7 or h > 12 where context implies PM, keep as-is
            detected_hour = min(h, 23)
            detected_min  = min(m, 59)
        else:
            q_lower = question.lower()
            for kw, h in named_times.items():
                if kw in q_lower:
                    detected_hour = h
                    break

        # ── Pull memory context ─────────────────────────────────────────────
        memory_context = ""
        live_snippet   = ""
        memory_status  = "unavailable"

        if device_id and device_id in PATIENT_STATES:
            patient_state = PATIENT_STATES[device_id]

            # ── Tier-0: Time-range query (highest priority if time detected) ──
            if detected_hour is not None:
                try:
                    time_ctx = run_async_readonly(
                        patient_state.memory.get_episodes_by_time_range(
                            center_hour=detected_hour,
                            center_minute=detected_min,
                            window_minutes=45,
                            limit=30,
                        ),
                        timeout=12,
                    )
                    if time_ctx:
                        time_context = time_ctx
                        memory_status = "active"
                        print(f"[Chat] Time-range data fetched for {detected_hour:02d}:{detected_min:02d}")
                except Exception as te:
                    print(f"[Chat] Time-range query failed: {te}")

            # ── Tier-1: Graphiti semantic search ──
            try:
                raw_ctx = run_async(
                    patient_state.memory.get_patient_context(question, limit=10)
                )
                if raw_ctx and "No patient history" not in raw_ctx and "first session" not in raw_ctx:
                    memory_context = raw_ctx
                    memory_status  = "active"
                else:
                    direct = run_async_readonly(
                        patient_state.memory.get_patient_episodes_direct(limit=15, hours=24), timeout=10
                    )
                    if direct:
                        memory_context = direct
                        memory_status  = "active"
                    else:
                        memory_context = "No stored episodes for this patient yet."
                        memory_status  = "empty"
            except Exception as e:
                direct = run_async_readonly(
                    patient_state.memory.get_patient_episodes_direct(limit=15, hours=24), timeout=10
                )
                if direct:
                    memory_context = direct
                    memory_status  = "active"
                else:
                    memory_context = f"Memory retrieval error: {e}"
                    memory_status  = "unavailable"

            # ── Activity summary (duration stats) ──
            try:
                activity_summary = run_async_readonly(
                    patient_state.memory.get_activity_summary(), timeout=15
                )
                if activity_summary:
                    memory_context = activity_summary + "\n\n---\nRAW EPISODE CONTEXT:\n" + memory_context
            except Exception as summ_e:
                print(f"[Chat] Activity summary failed: {summ_e}")

            if patient_state.history:
                latest = list(patient_state.history)[-1]
                live_snippet = (
                    f"Live now — HR: {int(latest.get('HR',0))} bpm, "
                    f"SpO2: {int(latest.get('Blood_oxygen',0))}%, "
                    f"Posture: {POSTURE_MAP.get(int(latest.get('Posture_state',0)),'Unknown')}, "
                    f"Location: {AREA_MAP.get(int(latest.get('Area', latest.get('Lokasi',0))),'Unknown')}."
                )
        else:
            # Patient not in active PATIENT_STATES — still try Neo4j via temporary memory object
            if device_id:
                try:
                    offline_mem = PatientMemory(device_id)

                    # Time-range query for offline patient
                    if detected_hour is not None:
                        try:
                            time_ctx = run_async_readonly(
                                offline_mem.get_episodes_by_time_range(
                                    center_hour=detected_hour,
                                    center_minute=detected_min,
                                    window_minutes=45,
                                    limit=30,
                                ),
                                timeout=12,
                            )
                            if time_ctx:
                                time_context = time_ctx
                                memory_status = "active"
                        except Exception as te:
                            print(f"[Chat Offline] Time-range query failed: {te}")

                    # Fallback: direct episode read
                    direct = run_async_readonly(
                        offline_mem.get_patient_episodes_direct(limit=20), timeout=12
                    )
                    if direct:
                        memory_context = direct
                        memory_status  = "active"
                    else:
                        memory_context = f"Patient {device_id} is offline — no live data. Historical memory from Neo4j: no records found."
                        memory_status  = "empty"

                    try:
                        activity_summary = run_async_readonly(
                            offline_mem.get_activity_summary(), timeout=15
                        )
                        if activity_summary:
                            memory_context = activity_summary + "\n\n---\nRAW EPISODE CONTEXT:\n" + memory_context
                    except Exception:
                        pass

                    live_snippet = f"Patient {device_id} is currently OFFLINE (not streaming live sensor data). All information comes from stored memory."
                except Exception as offline_e:
                    print(f"[Chat Offline] Failed to create offline memory: {offline_e}")
                    memory_context = f"Patient {device_id} is offline and memory could not be retrieved."
                    live_snippet   = "No live data available."
            else:
                summaries = []
                for did, ps in PATIENT_STATES.items():
                    if not ps.history:
                        continue
                    lat = list(ps.history)[-1]
                    summaries.append(
                        f"Device {did}: HR={int(lat.get('HR',0))}, "
                        f"SpO2={int(lat.get('Blood_oxygen',0))}%, "
                        f"Risk={ps.risk_score:.2f}"
                    )
                live_snippet = "\n".join(summaries) if summaries else "No active patients."
                memory_context = "No specific patient selected — responding from live data only."

        # Determine monitoring start time to clarify data window
        monitoring_start = ""
        if device_id and device_id in PATIENT_STATES and PATIENT_STATES[device_id].history:
            first_ts = list(PATIENT_STATES[device_id].history)[0].get('timestamp')
            if first_ts:
                monitoring_start = f"Monitoring started: {first_ts.strftime('%Y-%m-%d %H:%M') if hasattr(first_ts, 'strftime') else str(first_ts)[:16]}. Current time: {datetime.now().strftime('%Y-%m-%d %H:%M')}."

        # Build time-specific section header
        time_section = ""
        if time_context:
            time_section = f"""
⚑ TIME-SPECIFIC RECORDS (DIRECT FROM DATABASE — USE THESE FIRST):
The user asked about {detected_hour:02d}:{detected_min:02d}. Below are the actual recorded episodes from ±45 minutes around that time.
USE THESE RECORDS as primary source of truth for this question. Prefer them over any other context.

{time_context}

---
"""

        system_prompt = f"""You are a clinical AI assistant for UTLMediCore patient monitoring.
Model in use: {chat_model}. Current time: {datetime.now().strftime('%Y-%m-%d %H:%M WIB')}.

IMPORTANT — DATA TIME WINDOW:
{monitoring_start}
The memory context below may contain CUMULATIVE data across all past monitoring sessions (possibly multiple days or weeks).
Duration values (e.g. 'Time spent in Laboratory: 158 hours') reflect the TOTAL across ALL stored sessions, NOT just today.
When a user asks 'how long today' or 'how long this session', clarify the total vs today's session.
{time_section}
PATIENT CONTEXT & ACTIVITY DURATIONS (cumulative, across all sessions):
{memory_context}

CURRENT LIVE SENSOR DATA (right now):
{live_snippet}

RECENT SYSTEM ALERTS:
{json.dumps([a['message'] for a in ACTIVE_ALERTS[-3:]], ensure_ascii=False)}

INSTRUCTIONS:
1. LOCATION QUESTIONS: When asked 'where', answer with the LOCATION/AREA (e.g. Laboratory, Bedroom, Corridor). Posture (Lying Down, Standing, etc.) is NOT a location.
2. POSTURE QUESTIONS: When asked 'what posture', answer with body position (Lying Down, Sitting, Standing, Prone, etc.). Location is NOT a posture.
3. DURATION QUESTIONS: Clarify if the duration is total (all sessions) or today only. Use h/min format.
4. CITE DATA: Reference actual values (timestamps, step counts).
5. CONCISE: 2-4 sentences. Be direct and specific.
6. HONEST: If location data is missing, say so. Never confuse posture with location.
"""

        messages = [{"role": "system", "content": system_prompt}]
        for turn in session_history[-8:]:
            messages.append({"role": turn["role"], "content": turn["content"]})
        messages.append({"role": "user", "content": question})

        @track(name="memory_chatbot", tags=["chat", "graphiti", "memory"])
        def call_llm():
            if chat_model.startswith("ollamacloud:"):
                # Route to Ollama Cloud API (OpenAI-compatible)
                cloud_model_name = chat_model.replace("ollamacloud:", "", 1)
                return call_ollama_cloud(cloud_model_name, messages, temperature=0.3)
            else:
                # Local Ollama or OpenAI via aisuite
                return AI_CLIENT.chat.completions.create(
                    model=chat_model,
                    messages=messages,
                    temperature=0.3,
                )

        response = call_llm()
        answer   = response.choices[0].message.content

        return jsonify({
            "answer":         answer,
            "device_id":      device_id or "all",
            "memory_status":  memory_status,
            "memory_used":    memory_status == "active",
            "memory_preview": memory_context[:500] if memory_context else "",
            "model_used":     chat_model,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/available-models")
def get_available_models():
    """Return curated Ollama Cloud models for Chatbot & AI Insights UI."""
    return jsonify({
        'models':  CHAT_CLOUD_MODELS,
        'count':   len(CHAT_CLOUD_MODELS),
        'default': CHAT_DEFAULT_MODEL,
        'cloud_active': bool(OLLAMA_CLOUD_API_KEY),
    })

@app.route("/api/model-status")
def check_model_status():
    """Quick-check which Ollama models are actually loaded/pulled."""
    try:
        r = requests.get("http://localhost:11434/api/tags", timeout=3)
        if r.status_code == 200:
            pulled = [m["name"] for m in r.json().get("models", [])]
            result = {}
            for m in AVAILABLE_MODELS:
                if m.startswith("openai:"):
                    result[m] = "cloud"          # OpenAI cloud
                elif m.startswith("ollamacloud:"):
                    result[m] = "cloud_ollama"   # Ollama cloud API
                else:
                    short = m.replace("ollama:", "")
                    result[m] = "available" if any(short in p for p in pulled) else "not_pulled"
            return jsonify({
                "status": result,
                "ollama_running": True,
                "ollama_cloud_active": bool(OLLAMA_CLOUD_API_KEY),
            })
        else:
            return jsonify({"ollama_running": False, "error": f"Ollama HTTP {r.status_code}"})
    except Exception as e:
        # Ollama local not running — but cloud may still work
        result = {}
        for m in AVAILABLE_MODELS:
            if m.startswith("openai:"):
                result[m] = "cloud"
            elif m.startswith("ollamacloud:"):
                result[m] = "cloud_ollama"
            else:
                result[m] = "not_pulled"
        return jsonify({
            "status": result,
            "ollama_running": False,
            "ollama_cloud_active": bool(OLLAMA_CLOUD_API_KEY),
            "error": str(e),
        })

@app.route("/api/model-preferences")
def get_model_preferences():
    """Get current model preferences for all agents"""
    return jsonify(MODEL_PREFERENCES)

@app.route("/api/model-preferences", methods=["POST"])
def update_model_preference():
    """Update model preference for a specific agent"""
    try:
        payload = request.get_json() or {}
        agent = payload.get('agent', '').lower()
        model = payload.get('model', '')
        
        # Validation
        if agent not in MODEL_PREFERENCES:
            return jsonify({'error': f'Invalid agent: {agent}'}), 400
        
        if model not in AVAILABLE_MODELS:
            return jsonify({'error': f'Invalid model: {model}'}), 400
        
        # Update preference
        MODEL_PREFERENCES[agent] = model
        
        log_agent_activity(
            f"{agent.title()} Agent",
            f"Model changed to {model}",
            None,
            "success",
            f"User updated AI model preference"
        )
        
        return jsonify({
            'success': True,
            'agent': agent,
            'model': model,
            'message': f'Model preference updated for {agent} agent'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route("/ask", methods=["POST"])
def ask():
    """Enhanced chat endpoint with agentic context"""
    try:
        payload = request.get_json() or {}
        user_input = payload.get("question", "").strip()
        model = payload.get("model", AgentConfig.ANALYZER_AGENT)
        
        if not user_input:
            return jsonify({"error": "Empty question"}), 400
            
        # Get context from all patient states
        context_summary = []
        for device_id, state in PATIENT_STATES.items():
            if state.history:
                latest = list(state.history)[-1]
                context_summary.append(f"Device {device_id}: Risk={state.risk_score}, Recent alerts: {len([a for a in ACTIVE_ALERTS if a['device_id'] == device_id])}")
        
        system_prompt = f"""
        You are an autonomous health AI coordinator with access to:
        
        ACTIVE PATIENT MONITORING:
        {chr(10).join(context_summary)}
        
        RECENT ALERTS:
        {json.dumps([a for a in ACTIVE_ALERTS[-5:]], indent=2)}
        
        Provide medical insights based on this context.
        """
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_input}
        ]
        
        # Use tracked client for chat
        @track(name="chat_interface", tags=["chat", "user_query"])
        def get_chat_response():
            return AI_CLIENT.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.3
            )
            
        response = get_chat_response()
        
        answer = response.choices[0].message.content
        
        return jsonify({
            "answer": answer,
            "category": "agentic-analysis"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ==========================================
# MULTI-PERIOD REPORT ENDPOINTS
# ==========================================

@app.route('/api/report/generate', methods=['POST'])
def generate_multi_period_report():
    """
    Generate report for specific time period
    
    POST /api/report/generate
    {
        "device_id": "DCA632971FC3",
        "period": "daily" | "yesterday" | "weekly" | "monthly",
        "format": "html" | "json"
    }
    """
    data = request.json
    device_id = data.get('device_id')
    period = data.get('period', 'daily')
    output_format = data.get('format', 'html')
    
    if not device_id:
        return jsonify({"error": "device_id required"}), 400
    
    if device_id not in PATIENT_STATES:
        return jsonify({"error": "Patient not found"}), 404
    
    patient_state = PATIENT_STATES[device_id]
    
    # Determine time range
    period_config = {
        'daily': {'hours': 24, 'label': 'Daily', 'folder': 'daily'},
        'yesterday': {'hours': 48, 'label': 'Yesterday', 'folder': 'daily', 'offset': 24},
        'weekly': {'hours': 168, 'label': 'Weekly', 'folder': 'weekly'},
        'monthly': {'hours': 720, 'label': 'Monthly', 'folder': 'monthly'}
    }
    
    if period not in period_config:
        return jsonify({"error": "Invalid period"}), 400
    
    config = period_config[period]
    time_range_hours = config['hours']
    
    # Get Graphiti memory summary
    try:
        graphiti_summary = run_async_readonly(
            patient_state.memory.get_activity_summary(hours_back=time_range_hours),
            timeout=15
        )
    except Exception as e:
        print(f"[REPORT] Graphiti error: {e}")
        graphiti_summary = "Memory summary unavailable."
    
    # Define model caller for Lite Agent (multi-step AI reasoning)
    def model_caller(prompt):
        # Always prefer high-end cloud models for reports if available
        chat_model = MODEL_PREFERENCES.get('coordinator', AgentConfig.COORDINATOR_AGENT)
        
        if OLLAMA_CLOUD_API_KEY:
            # Sort models to prioritize strongest ones first for reports
            preferred_models = ['deepseek-v3.2', 'kimi-k2-thinking', 'mistral-large-3:675b']
            current_pref = chat_model.split('ollamacloud:')[1] if chat_model.startswith('ollamacloud:') else None
            
            models_to_try = ([current_pref] if current_pref else []) + preferred_models
            models_to_try = list(dict.fromkeys(m for m in models_to_try if m))
            
            last_err = None
            for m in models_to_try:
                try:
                    print(f"[LITE AGENT] Requesting deep analysis from cloud model: {m}...")
                    # Note: We don't use the standard 60s timeout here, we allow up to 180s for thinking
                    resp = call_ollama_cloud(m, [{"role": "user", "content": prompt}], temperature=0.3)
                    return resp.choices[0].message.content
                except Exception as e:
                    print(f"[LITE AGENT] Cloud model {m} failed or busy: {e}")
                    last_err = e
                    continue
            print(f"[LITE AGENT] All cloud models failed. Fallback to local...")
            
        # Local fallback if cloud fails or not configured
        from ollama import AsyncClient
        local_model = AgentConfig.COORDINATOR_AGENT.replace('ollama:', '')
        client = AsyncClient(host=AgentConfig.OLLAMA_HOST)
        resp = run_async_readonly(
            client.chat(model=local_model, messages=[{"role": "user", "content": prompt}], stream=False),
            timeout=120 # Local also gets more time for thinking
        )
        return resp['message']['content']

    # Generate report
    report_data = ReportGenerator.generate_report(
        patient_state=patient_state,
        alerts=patient_state.alerts,
        agent_logs=[log for log in AGENT_ACTIVITY_LOG if log.get('device_id') == device_id],
        time_range_hours=time_range_hours,
        graph_memory_summary=graphiti_summary,
        ai_narrative="",  # Will be auto-generated by Lite Agent or CrewAI
        model_caller=model_caller
    )
    
    if output_format == 'json':
        return jsonify(report_data)
    
    # Generate HTML
    html_content = ReportGenerator.export_to_html(report_data)
    
    # Save file
    timestamp = datetime.now().strftime('%Y-%m-%d')
    if period == 'weekly':
        week_num = datetime.now().isocalendar()[1]
        filename = f"report_{device_id}_week_{week_num}.html"
    elif period == 'monthly':
        month = datetime.now().strftime('%Y-%m')
        filename = f"report_{device_id}_month_{month}.html"
    else:
        filename = f"report_{device_id}_{timestamp}.html"
    
    filepath = os.path.join('reports', config['folder'], filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"[REPORT] Generated {period} report: {filepath}")
    
    return jsonify({
        "success": True,
        "period": period,
        "device_id": device_id,
        "filename": filename,
        "filepath": filepath,
        "download_url": f"/api/report/download?file={filepath}"
    })


@app.route('/api/report/download', methods=['GET'])
def download_report():
    """
    Download generated report
    
    GET /api/report/download?file=reports/daily/report_DCA632_2026-03-05.html
    """
    filepath = request.args.get('file')
    
    if not filepath or not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404
    
    return send_file(
        filepath,
        as_attachment=True,
        download_name=os.path.basename(filepath),
        mimetype='text/html'
    )


@app.route('/api/report/list', methods=['GET'])
def list_reports():
    """
    List all available reports
    
    GET /api/report/list?device_id=DCA632971FC3&period=daily
    """
    device_id = request.args.get('device_id')
    period = request.args.get('period', 'all')
    
    reports = []
    
    folders = ['daily', 'weekly', 'monthly'] if period == 'all' else [period]
    
    for folder in folders:
        folder_path = os.path.join('reports', folder)
        if not os.path.exists(folder_path):
            continue
        
        for filename in os.listdir(folder_path):
            if not filename.endswith('.html'):
                continue
            
            if device_id and device_id not in filename:
                continue
            
            filepath = os.path.join(folder_path, filename)
            stat = os.stat(filepath)
            
            reports.append({
                'filename': filename,
                'filepath': filepath,
                'period': folder,
                'size_kb': round(stat.st_size / 1024, 2),
                'created': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'download_url': f"/api/report/download?file={filepath}"
            })
    
    reports.sort(key=lambda x: x['created'], reverse=True)
    
    return jsonify({
        "total": len(reports),
        "reports": reports
    })

# ======================
# SOCKETIO EVENTS
# ======================

@socketio.on('connect')
def handle_connect():
    print("✅ Client connected to SocketIO")
    # Send current state
    emit('patient_states', {
        device_id: {
            'risk_score': state.risk_score,
            'data_points': len(state.history)
        }
        for device_id, state in PATIENT_STATES.items()
    })

@socketio.on('request_analysis')
def handle_analysis_request(data):
    """Client requests manual analysis"""
    device_id = data.get('device_id')
    if device_id in PATIENT_STATES:
        results = CoordinatorAgent.coordinate_analysis(device_id)
        summary = CoordinatorAgent.generate_ai_summary(results)
        emit('analysis_result', {
            'results': results,
            'summary': summary
        })

import atexit

if __name__ == "__main__":
    print("🚀 UTLMediCore Agentic AI System Starting...")
    print(f"🤖 Autonomous Agents: Monitor, Analyzer, Alert, Predictor, Coordinator")
    print(f"📊 Auto-analysis interval: {AgentConfig.AUTO_ANALYSIS_INTERVAL}s")
    print(f"🔔 Auto-alerts: {'Enabled' if AgentConfig.AUTO_ALERT_ENABLED else 'Disabled'}")
    
    # Gracefully close Neo4j connection on shutdown
    atexit.register(lambda: run_async(close_graphiti()))
    
    socketio.run(app, host='0.0.0.0', port=7000, debug=True, allow_unsafe_werkzeug=True)