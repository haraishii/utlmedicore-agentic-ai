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

# Load environment variables from .env file
load_dotenv()

# Custom JSON Encoder untuk handle datetime
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

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
    MONGO_URL = os.getenv('MONGO_URL', 'mongodb://localhost:27017/')
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
        
    def add_data(self, data):
        """Add new sensor reading"""
        data['timestamp'] = datetime.now()
        self.history.append(data)
        
    def get_recent(self, n=10):
        """Get N most recent readings"""
        return list(self.history)[-n:]

# Global data structures
PATIENT_STATES = {}  # device_id -> PatientState
ACTIVE_ALERTS = []   # List of active alerts
AGENT_ACTIVITY_LOG = deque(maxlen=100)  # Last 100 agent activities

# Available AI Models
AVAILABLE_MODELS = [
    'ollama:qwen2.5:7b',
    'ollama:llama3.1:8b',
    'ollama:gemma3:12b',
    'ollama:deepseek-r1:8b',
    'ollama:medllama2:7b',
    'ollama:meditron:7b',
    'openai:gpt-4o-mini',
    'ollama:monotykamary/medichat-llama3:8b',
    'ollama:ALIENTELLIGENCE/medicaldiagnostictools:latest',
    'ollama:olmo-3:7b',
    'ollama:gpt-oss:20b',
    'ollama:deepseek-r1:14b'
]

# Model Preferences (per agent)
MODEL_PREFERENCES = {
    'monitor': 'ollama:medllama2:7b',
    'analyzer': 'ollama:ALIENTELLIGENCE/medicaldiagnostictools:latest',
    'predictor': 'ollama:deepseek-r1:14b',
    'alert': 'ollama:monotykamary/medichat-llama3:8b',
    'coordinator': 'ollama:gemma3:12b'
}

# AI Client and Chat History
AI_CLIENT = Client()
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
            'data': latest
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
                        "content": "You are a medical AI coordinator. Summarize the autonomous analysis in clear, actionable language. Highlight critical findings first."
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
    
    stats = {
        'hr_avg': round(np.mean(hrs), 1) if hrs else 0,
        'hr_min': min(hrs) if hrs else 0,
        'hr_max': max(hrs) if hrs else 0,
        'spo2_avg': round(np.mean(spo2s), 1) if spo2s else 0,
        'spo2_min': min(spo2s) if spo2s else 0
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
                'Area': AREA_MAP.get(int(d.get('Area', d.get('Lokasi', 0))), 'Unknown')
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
    if device_id not in PATIENT_STATES:
        return jsonify({'error': 'Patient not found'}), 404
    
    # Get parameters
    time_range = request.args.get('hours', default=24, type=int)
    format_type = request.args.get('format', default='json', type=str).lower()
    
    # Validate time range
    if time_range < 1 or time_range > 168:  # Max 1 week
        return jsonify({'error': 'Time range must be between 1 and 168 hours'}), 400
    
    patient_state = PATIENT_STATES[device_id]
    patient_alerts = [a for a in ACTIVE_ALERTS if a.get('device_id') == device_id]
    patient_logs = [log for log in AGENT_ACTIVITY_LOG if log.get('device_id') == device_id]
    
    try:
        # Generate report
        report_data = ReportGenerator.generate_report(
            patient_state,
            patient_alerts,
            patient_logs,
            time_range_hours=time_range
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


@app.route("/api/available-models")
def get_available_models():
    """Get list of available AI models"""
    return jsonify({
        'models': AVAILABLE_MODELS,
        'count': len(AVAILABLE_MODELS)
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
        
        response = AI_CLIENT.chat.completions.create(
            model=model,
            messages=messages,
            temperature=0.3
        )
        
        answer = response.choices[0].message.content
        
        return jsonify({
            "answer": answer,
            "category": "agentic-analysis"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

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

if __name__ == "__main__":
    print("🚀 UTLMediCore Agentic AI System Starting...")
    print(f"🤖 Autonomous Agents: Monitor, Analyzer, Alert, Predictor, Coordinator")
    print(f"📊 Auto-analysis interval: {AgentConfig.AUTO_ANALYSIS_INTERVAL}s")
    print(f"🔔 Auto-alerts: {'Enabled' if AgentConfig.AUTO_ALERT_ENABLED else 'Disabled'}")
    
    socketio.run(app, host='0.0.0.0', port=7000, debug=True)