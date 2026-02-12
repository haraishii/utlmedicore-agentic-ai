"""
Additional Test Datasets for Alert and Coordinator Agents
==========================================================

This module provides test cases for Alert and Coordinator agent evaluation.

Usage:
    from evaluation.test_datasets_extended import ALERT_CLASSIFICATION_TESTS, COORDINATOR_DECISION_TESTS
"""

from datetime import datetime


# ======================
# ALERT AGENT TESTS (15 cases)
# ======================

ALERT_CLASSIFICATION_TESTS = [
    # CRITICAL ALERTS (5 cases)
    {
        "id": "ALERT_CRIT_001",
        "description": "Fall with hypoxia - immediate response",
        "category": "critical",
        "input_data": {
            "event_type": "FALL_DETECTED",
            "patient_id": "P001",
            "HR": 125,
            "Blood_oxygen": 82,
            "Posture_state": 5,
            "Area": 6,  # Bathroom
            "additional_anomalies": ["HYPOXIA", "TACHYCARDIA"],
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "alert_level": "CRITICAL",
            "urgency_score": 0.95,
            "requires_immediate_action": True
        },
        "ground_truth_label": 2  # 2 = critical
    },
    {
        "id": "ALERT_CRIT_002",
        "description": "Severe bradycardia with fall",
        "category": "critical",
        "input_data": {
            "event_type": "FALL_DETECTED",
            "patient_id": "P002",
            "HR": 32,
            "Blood_oxygen": 88,
            "Posture_state": 5,
            "Area": 4,
            "additional_anomalies": ["BRADYCARDIA"],
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "alert_level": "CRITICAL",
            "urgency_score": 0.98
        },
        "ground_truth_label": 2
    },
    {
        "id": "ALERT_CRIT_003",
        "description": "Repeated falls within 1 hour",
        "category": "critical",
        "input_data": {
            "event_type": "MULTIPLE_FALLS",
            "patient_id": "P003",
            "fall_count": 3,
            "time_window_minutes": 60,
            "last_fall_severity": "CRITICAL",
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "alert_level": "CRITICAL",
            "urgency_score": 0.92
        },
        "ground_truth_label": 2
    },
    {
        "id": "ALERT_CRIT_004",
        "description": "Sudden severe hypoxia",
        "category": "critical",
        "input_data": {
            "event_type": "VITAL_SIGN_ANOMALY",
            "patient_id": "P004",
            "HR": 110,
            "Blood_oxygen": 75,
            "Posture_state": 2,
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "alert_level": "CRITICAL",
            "urgency_score": 0.96
        },
        "ground_truth_label": 2
    },
    {
        "id": "ALERT_CRIT_005",
        "description": "High risk score with anomaly",
        "category": "critical",
        "input_data": {
            "event_type": "RISK_ESCALATION",
            "patient_id": "P005",
            "risk_score": 0.89,
            "risk_category": "HIGH",
            "recent_anomalies": ["TACHYCARDIA", "HYPOXIA"],
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "alert_level": "CRITICAL",
            "urgency_score": 0.85
        },
        "ground_truth_label": 2
    },
    
    # WARNING ALERTS (5 cases)
    {
        "id": "ALERT_WARN_001",
        "description": "Moderate tachycardia at rest",
        "category": "warning",
        "input_data": {
            "event_type": "VITAL_SIGN_ANOMALY",
            "patient_id": "P006",
            "HR": 122,
            "Blood_oxygen": 94,
            "Posture_state": 1,
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "alert_level": "WARNING",
            "urgency_score": 0.55,
            "requires_immediate_action": False
        },
        "ground_truth_label": 1  # 1 = warning
    },
    {
        "id": "ALERT_WARN_002",
        "description": "Lying in bathroom (high risk context)",
        "category": "warning",
        "input_data": {
            "event_type": "CONTEXTUAL_RISK",
            "patient_id": "P007",
            "HR": 88,
            "Blood_oxygen": 95,
            "Posture_state": 3,
            "Area": 6,
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "alert_level": "WARNING",
            "urgency_score": 0.65
        },
        "ground_truth_label": 1
    },
    {
        "id": "ALERT_WARN_003",
        "description": "Mild hypoxia",
        "category": "warning",
        "input_data": {
            "event_type": "VITAL_SIGN_ANOMALY",
            "patient_id": "P008",
            "HR": 85,
            "Blood_oxygen": 88,
            "Posture_state": 1,
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "alert_level": "WARNING",
            "urgency_score": 0.60
        },
        "ground_truth_label": 1
    },
    {
        "id": "ALERT_WARN_004",
        "description": "Medium risk score trending up",
        "category": "warning",
        "input_data": {
            "event_type": "RISK_TREND",
            "patient_id": "P009",
            "risk_score": 0.52,
            "risk_category": "MEDIUM",
            "trend": "INCREASING",
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "alert_level": "WARNING",
            "urgency_score": 0.50
        },
        "ground_truth_label": 1
    },
    {
        "id": "ALERT_WARN_005",
        "description": "Unusual activity pattern",
        "category": "warning",
        "input_data": {
            "event_type": "PATTERN_ANOMALY",
            "patient_id": "P010",
            "anomaly_description": "Nocturnal wandering",
            "confidence": 0.75,
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "alert_level": "WARNING",
            "urgency_score": 0.45
        },
        "ground_truth_label": 1
    },
    
    # INFO/NO ALERT (5 cases)
    {
        "id": "ALERT_INFO_001",
        "description": "Normal vitals, routine check",
        "category": "info",
        "input_data": {
            "event_type": "ROUTINE_CHECK",
            "patient_id": "P011",
            "HR": 75,
            "Blood_oxygen": 97,
            "Posture_state": 1,
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "alert_level": "INFO",
            "urgency_score": 0.05,
            "requires_immediate_action": False
        },
        "ground_truth_label": 0  # 0 = no alert
    },
    {
        "id": "ALERT_INFO_002",
        "description": "Low risk patient, stable",
        "category": "info",
        "input_data": {
            "event_type": "RISK_UPDATE",
            "patient_id": "P012",
            "risk_score": 0.12,
            "risk_category": "LOW",
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "alert_level": "INFO",
            "urgency_score": 0.10
        },
        "ground_truth_label": 0
    },
    {
        "id": "ALERT_INFO_003",
        "description": "Exercise-induced elevated HR (expected)",
        "category": "info",
        "input_data": {
            "event_type": "VITAL_SIGN_CHECK",
            "patient_id": "P013",
            "HR": 118,
            "Blood_oxygen": 95,
            "Posture_state": 8,
            "Step": 150,
            "context": "exercise",
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "alert_level": "INFO",
            "urgency_score": 0.15
        },
        "ground_truth_label": 0
    },
    {
        "id": "ALERT_INFO_004",
        "description": "Sleeping - low HR expected",
        "category": "info",
        "input_data": {
            "event_type": "VITAL_SIGN_CHECK",
            "patient_id": "P014",
            "HR": 58,
            "Blood_oxygen": 96,
            "Posture_state": 3,
            "Area": 1,
            "context": "sleeping",
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "alert_level": "INFO",
            "urgency_score": 0.08
        },
        "ground_truth_label": 0
    },
    {
        "id": "ALERT_INFO_005",
        "description": "Routine position change",
        "category": "info",
        "input_data": {
            "event_type": "POSTURE_CHANGE",
            "patient_id": "P015",
            "from_posture": 1,
            "to_posture": 2,
            "HR": 92,
            "Blood_oxygen": 96,
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "alert_level": "INFO",
            "urgency_score": 0.05
        },
        "ground_truth_label": 0
    }
]


# ======================
# COORDINATOR AGENT TESTS (15 cases)
# ======================

COORDINATOR_DECISION_TESTS = [
    # EMERGENCY COORDINATION (5 cases)
    {
        "id": "COORD_001",
        "description": "Fall detected - coordinate emergency response",
        "category": "emergency",
        "input_data": {
            "monitor_output": {"fall_detected": True, "severity": "CRITICAL"},
            "analyzer_output": {"patient_history": "2 previous falls this week"},
            "predictor_output": {"injury_risk": 0.88},
            "alert_output": {"alert_level": "CRITICAL", "urgency_score": 0.95}
        },
        "expected_output": {
            "decision": "EMERGENCY_RESPONSE",
            "priority": "HIGHEST"
        },
        "ground_truth_decision": "EMERGENCY_RESPONSE"
    },
    {
        "id": "COORD_002",
        "description": "Moderate risk - schedule check-in",
        "category": "routine",
        "input_data": {
            "monitor_output": {"fall_detected": False, "severity": "WARNING"},
            "analyzer_output": {"pattern": "elevated_hr_trend"},
            "predictor_output": {"risk_score": 0.48},
            "alert_output": {"alert_level": "WARNING", "urgency_score": 0.50}
        },
        "expected_output": {
            "decision": "SCHEDULED_CHECK",
            "priority": "MEDIUM"
        },
        "ground_truth_decision": "SCHEDULED_CHECK"
    },
    {
        "id": "COORD_003",
        "description": "Conflicting outputs - verify needed",
        "category": "conflict",
        "input_data": {
            "monitor_output": {"fall_detected": True, "confidence": 0.65},
            "analyzer_output": {"context": "exercising", "likely_false_positive": True},
            "predictor_output": {"injury_risk": 0.15},
            "alert_output": {"alert_level": "WARNING", "urgency_score": 0.45}
        },
        "expected_output": {
            "decision": "VERIFY_WITH_NURSE",
            "priority": "MEDIUM"
        },
        "ground_truth_decision": "VERIFY_WITH_NURSE"
    },
    {
        "id": "COORD_004",
        "description": "All normal - continue monitoring",
        "category": "routine",
        "input_data": {
            "monitor_output": {"fall_detected": False, "severity": "NORMAL"},
            "analyzer_output": {"pattern": "normal_activity"},
            "predictor_output": {"risk_score": 0.08},
            "alert_output": {"alert_level": "INFO", "urgency_score": 0.05}
        },
        "expected_output": {
            "decision": "CONTINUE_MONITORING",
            "priority": "LOW"
        },
        "ground_truth_decision": "CONTINUE_MONITORING"
    },
    {
        "id": "COORD_005",
        "description": "High risk prediction - preventive action",
        "category": "preventive",
        "input_data": {
            "monitor_output": {"fall_detected": False, "severity": "NORMAL"},
            "analyzer_output": {"trend": "WORSENING"},
            "predictor_output": {"predicted_fall_risk_24h": 0.82},
            "alert_output": {"alert_level": "WARNING", "urgency_score": 0.60}
        },
        "expected_output": {
            "decision": "PREVENTIVE_INTERVENTION",
            "priority": "HIGH"
        },
        "ground_truth_decision": "PREVENTIVE_INTERVENTION"
    },
    
    # MULTI-PATIENT SCENARIOS (5 cases)
    {
        "id": "COORD_006",
        "description": "3 patients - prioritization needed",
        "category": "prioritization",
        "input_data": {
            "patient_alerts": [
                {"patient_id": "P001", "alert_level": "CRITICAL", "urgency": 0.95},
                {"patient_id": "P002", "alert_level": "WARNING", "urgency": 0.55},
                {"patient_id": "P003", "alert_level": "WARNING", "urgency": 0.48}
            ],
            "available_nurses": 2
        },
        "expected_output": {
            "decision": "PRIORITIZE_RESOURCES",
            "priority_order": ["P001", "P002", "P003"]
        },
        "ground_truth_decision": "PRIORITIZE_RESOURCES"
    },
    {
        "id": "COORD_007",
        "description": "2 critical patients simultaneously",
        "category": "resource_allocation",
        "input_data": {
            "patient_alerts": [
                {"patient_id": "P001", "alert_level": "CRITICAL", "urgency": 0.95, "event": "fall"},
                {"patient_id": "P005", "alert_level": "CRITICAL", "urgency": 0.92, "event": "hypoxia"}
            ],
            "available_nurses": 2
        },
        "expected_output": {
            "decision": "SPLIT_EMERGENCY_RESPONSE",
            "priority": "HIGHEST"
        },
        "ground_truth_decision": "SPLIT_EMERGENCY_RESPONSE"
    },
    
    # ERROR HANDLING (5 cases)
    {
        "id": "COORD_EDGE_001",
        "description": "Sensor malfunction - ignore bad data",
        "category": "error_handling",
        "input_data": {
            "monitor_output": {"fall_detected": True, "HR": 255, "Blood_oxygen": 0, "data_quality": "POOR"},
            "analyzer_output": {"data_reliability": "LOW", "likely_sensor_error": True}
        },
        "expected_output": {
            "decision": "IGNORE_BAD_DATA",
            "priority": "MEDIUM"
        },
        "ground_truth_decision": "IGNORE_BAD_DATA"
    },
    {
        "id": "COORD_EDGE_002",
        "description": "Agent timeout - proceed with available",
        "category": "partial_data",
        "input_data": {
            "monitor_output": {"fall_detected": True, "severity": "CRITICAL"},
            "analyzer_output": "TIMEOUT",
            "predictor_output": "TIMEOUT",
            "alert_output": {"alert_level": "CRITICAL", "urgency_score": 0.90}
        },
        "expected_output": {
            "decision": "PROCEED_WITH_AVAILABLE_DATA",
            "priority": "HIGHEST"
        },
        "ground_truth_decision": "PROCEED_WITH_AVAILABLE_DATA"
    },
    
    # SYSTEM HEALTH (3 cases)
    {
        "id": "COORD_SYS_001",
        "description": "All agents healthy - optimal",
        "category": "system_health",
        "input_data": {
            "system_status": {
                "monitor_agent": {"status": "healthy", "latency_ms": 120},
                "analyzer_agent": {"status": "healthy", "latency_ms": 1500},
                "predictor_agent": {"status": "healthy", "latency_ms": 1800},
                "alert_agent": {"status": "healthy", "latency_ms": 900}
            }
        },
        "expected_output": {
            "system_health": "OPTIMAL"
        },
        "ground_truth_decision": "CONTINUE_MONITORING"
    },
    {
        "id": "COORD_SYS_002",
        "description": "High load - throttle non-critical",
        "category": "load_balancing",
        "input_data": {
            "system_status": {
                "monitor_agent": {"status": "degraded", "latency_ms": 5200},
                "predictor_agent": {"status": "degraded", "latency_ms": 8000}
            },
            "active_patients": 45,
            "pending_alerts": 18
        },
        "expected_output": {
            "decision": "THROTTLE_NON_CRITICAL",
            "system_health": "DEGRADED"
        },
        "ground_truth_decision": "THROTTLE_NON_CRITICAL"
    },
    {
        "id": "COORD_SYS_003",
        "description": "Agent failure - activate fallback",
        "category": "failover",
        "input_data": {
            "system_status": {
                "monitor_agent": {"status": "failed", "error": "connection_lost"},
                "analyzer_agent": {"status": "healthy"},
                "predictor_agent": {"status": "healthy"}
            }
        },
        "expected_output": {
            "decision": "ACTIVATE_FALLBACK_MONITOR",
            "system_health": "DEGRADED"
        },
        "ground_truth_decision": "ACTIVATE_FALLBACK_MONITOR"
    }
]


# Export
__all__ = [
    "ALERT_CLASSIFICATION_TESTS",
    "COORDINATOR_DECISION_TESTS"
]
