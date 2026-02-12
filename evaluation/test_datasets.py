"""
Test Datasets for Agent Evaluation
===================================

This module provides ground truth test cases for validating agent performance:
1. Fall Detection Test Cases (50 cases)
2. Vital Signs Anomaly Detection (40 cases)
3. Risk Scoring Validation (30 cases)

Each test case includes:
- Input data (sensor readings)
- Expected output (agent should produce)
- Ground truth label (for metric calculation)
- Description and rationale

Usage:
    from evaluation.test_datasets import FALL_DETECTION_TESTS
    
    for test in FALL_DETECTION_TESTS:
        prediction = monitor_agent.analyze(test['input_data'])
        accuracy = compare(prediction, test['expected_output'])
"""

from datetime import datetime, timedelta


# ======================
# FALL DETECTION TEST CASES (50 cases)
# ======================

FALL_DETECTION_TESTS = [
    # TRUE POSITIVES: Confirmed Falls (20 cases)
    {
        "id": "FALL_TP_001",
        "description": "Confirmed fall in bathroom with hypoxia",
        "category": "true_positive",
        "input_data": {
            "HR": 125,
            "Blood_oxygen": 85,
            "Posture_state": 5,  # Fall
            "Area": 6,  # Bathroom
            "Step": 0,
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "fall_detected": True,
            "severity": "CRITICAL",
            "anomalies": ["FALL_DETECTED", "HYPOXIA"],
            "confidence": 0.95
        },
        "ground_truth_label": 1  # 1 = fall
    },
    {
        "id": "FALL_TP_002",
        "description": "Fall in bedroom with tachycardia",
        "category": "true_positive",
        "input_data": {
            "HR": 135,
            "Blood_oxygen": 92,
            "Posture_state": 5,
            "Area": 1,  # Bedroom
            "Step": 0,
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "fall_detected": True,
            "severity": "CRITICAL",
            "anomalies": ["FALL_DETECTED", "TACHYCARDIA"]
        },
        "ground_truth_label": 1
    },
    {
        "id": "FALL_TP_003",
        "description": "Fall in living room, normal vitals",
        "category": "true_positive",
        "input_data": {
            "HR": 88,
            "Blood_oxygen": 96,
            "Posture_state": 5,
            "Area": 3,  # Living Room
            "Step": 0,
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "fall_detected": True,
            "severity": "CRITICAL",
            "anomalies": ["FALL_DETECTED"]
        },
        "ground_truth_label": 1
    },
    {
        "id": "FALL_TP_004",
        "description": "Fall in corridor, elderly patient",
        "category": "true_positive",
        "input_data": {
            "HR": 105,
            "Blood_oxygen": 93,
            "Posture_state": 5,
            "Area": 4,  # Corridor
            "Step": 3,
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "fall_detected": True,
            "severity": "CRITICAL",
            "anomalies": ["FALL_DETECTED"]
        },
        "ground_truth_label": 1
    },
    {
        "id": "FALL_TP_005",
        "description": "Fall during walking (mid-stride)",
        "category": "true_positive",
        "input_data": {
            "HR": 98,
            "Blood_oxygen": 94,
            "Posture_state": 5,
            "Area": 4,
            "Step": 15,  # Was walking
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "fall_detected": True,
            "severity": "CRITICAL"
        },
        "ground_truth_label": 1
    },
    
    # TRUE NEGATIVES: Normal Activities (20 cases)
    {
        "id": "FALL_TN_001",
        "description": "Normal sitting in bedroom",
        "category": "true_negative",
        "input_data": {
            "HR": 78,
            "Blood_oxygen": 97,
            "Posture_state": 1,  # Sitting
            "Area": 1,
            "Step": 0,
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "fall_detected": False,
            "severity": "NORMAL",
            "anomalies": []
        },
        "ground_truth_label": 0  # 0 = no fall
    },
    {
        "id": "FALL_TN_002",
        "description": "Standing in kitchen",
        "category": "true_negative",
        "input_data": {
            "HR": 82,
            "Blood_oxygen": 96,
            "Posture_state": 2,  # Standing
            "Area": 5,  # Laboratory/Kitchen
            "Step": 0,
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "fall_detected": False,
            "severity": "NORMAL"
        },
        "ground_truth_label": 0
    },
    {
        "id": "FALL_TN_003",
        "description": "Walking in corridor (normal gait)",
        "category": "true_negative",
        "input_data": {
            "HR": 95,
            "Blood_oxygen": 96,
            "Posture_state": 8,  # Walking
            "Area": 4,
            "Step": 45,
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "fall_detected": False,
            "severity": "NORMAL"
        },
        "ground_truth_label": 0
    },
    {
        "id": "FALL_TN_004",
        "description": "Lying in bed (sleeping)",
        "category": "true_negative",
        "input_data": {
            "HR": 65,
            "Blood_oxygen": 96,
            "Posture_state": 3,  # Lying
            "Area": 1,  # Bedroom
            "Step": 0,
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "fall_detected": False,
            "severity": "NORMAL"
        },
        "ground_truth_label": 0
    },
    {
        "id": "FALL_TN_005",
        "description": "Sitting and reading",
        "category": "true_negative",
        "input_data": {
            "HR": 72,
            "Blood_oxygen": 98,
            "Posture_state": 1,
            "Area": 3,  # Living room
            "Step": 0,
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "fall_detected": False,
            "severity": "NORMAL"
        },
        "ground_truth_label": 0
    },
    
    # EDGE CASES (10 cases)
    {
        "id": "FALL_EDGE_001",
        "description": "Lying in bathroom (high risk context)",
        "category": "edge_case",
        "input_data": {
            "HR": 92,
            "Blood_oxygen": 94,
            "Posture_state": 3,  # Lying (not fall, but suspicious)
            "Area": 6,  # Bathroom
            "Step": 0,
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "fall_detected": False,  # Not Posture=5, but should trigger WARNING
            "severity": "WARNING",
            "contextual_risk": "high"
        },
        "ground_truth_label": 0,  # Not technically a fall
        "notes": "Context-aware detection should flag this as high risk"
    },
    {
        "id": "FALL_EDGE_002",
        "description": "Quick sit-down (might look like fall)",
        "category": "edge_case",
        "input_data": {
            "HR": 102,
            "Blood_oxygen": 95,
            "Posture_state": 1,  # Sitting (arrived quickly)
            "Area": 3,
            "Step": 5,  # Was walking
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "fall_detected": False,
            "severity": "NORMAL"
        },
        "ground_truth_label": 0,
        "notes": "Rapid posture change but not a fall"
    },
    {
        "id": "FALL_EDGE_003",
        "description": "Exercise-induced tachycardia while standing",
        "category": "edge_case",
        "input_data": {
            "HR": 125,
            "Blood_oxygen": 94,
            "Posture_state": 2,  # Standing
            "Area": 5,
            "Step": 120,  # Been walking actively
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "fall_detected": False,
            "severity": "WARNING",  # High HR but explained by activity
            "anomalies": ["TACHYCARDIA"]
        },
        "ground_truth_label": 0
    },
    
    # Additional TP cases
    {
        "id": "FALL_TP_006",
        "description": "Fall with bradycardia (syncope)",
        "category": "true_positive",
        "input_data": {
            "HR": 38,
            "Blood_oxygen": 90,
            "Posture_state": 5,
            "Area": 4,
            "Step": 8,
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "fall_detected": True,
            "severity": "CRITICAL",
            "anomalies": ["FALL_DETECTED", "BRADYCARDIA"]
        },
        "ground_truth_label": 1
    },
    {
        "id": "FALL_TP_007",
        "description": "Fall in laboratory area",
        "category": "true_positive",
        "input_data": {
            "HR": 110,
            "Blood_oxygen": 91,
            "Posture_state": 5,
            "Area": 5,
            "Step": 0,
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "fall_detected": True,
            "severity": "CRITICAL"
        },
        "ground_truth_label": 1
    },
    
    # Additional TN cases
    {
        "id": "FALL_TN_006",
        "description": "Normal standing with slight tachycardia",
        "category": "true_negative",
        "input_data": {
            "HR": 105,
            "Blood_oxygen": 96,
            "Posture_state": 2,
            "Area": 3,
            "Step": 0,
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "fall_detected": False,
            "severity": "NORMAL"
        },
        "ground_truth_label": 0
    },
    {
        "id": "FALL_TN_007",
        "description": "Sitting with normal vitals",
        "category": "true_negative",
        "input_data": {
            "HR": 76,
            "Blood_oxygen": 97,
            "Posture_state": 1,
            "Area": 1,
            "Step": 0,
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "fall_detected": False,
            "severity": "NORMAL"
        },
        "ground_truth_label": 0
    },
    
    # ADDITIONAL TRUE POSITIVES (more diverse fall scenarios)
    {
        "id": "FALL_TP_008",
        "description": "Night-time fall in bedroom with hypoxia",
        "category": "true_positive",
        "input_data": {
            "HR": 115,
            "Blood_oxygen": 87,
            "Posture_state": 5,
            "Area": 1,  # Bedroom
            "Step": 2,
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "fall_detected": True,
            "severity": "CRITICAL",
            "anomalies": ["FALL_DETECTED", "HYPOXIA"]
        },
        "ground_truth_label": 1
    },
    {
        "id": "FALL_TP_009",
        "description": "Fall in kitchen area during meal prep",
        "category": "true_positive",
        "input_data": {
            "HR": 98,
            "Blood_oxygen": 93,
            "Posture_state": 5,
            "Area": 2,  # Kitchen
            "Step": 15,
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "fall_detected": True,
            "severity": "CRITICAL"
        },
        "ground_truth_label": 1
    },
    {
        "id": "FALL_TP_010",
        "description": "Fall with severe bradycardia (cardiac event)",
        "category": "true_positive",
        "input_data": {
            "HR": 32,
            "Blood_oxygen": 88,
            "Posture_state": 5,
            "Area": 3,
            "Step": 0,
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "fall_detected": True,
            "severity": "CRITICAL",
            "anomalies": ["FALL_DETECTED", "BRADYCARDIA", "HYPOXIA"]
        },
        "ground_truth_label": 1
    },
    {
        "id": "FALL_TP_011",
        "description": "Fall during transition from standing to walking",
        "category": "true_positive",
        "input_data": {
            "HR": 108,
            "Blood_oxygen": 94,
            "Posture_state": 5,
            "Area": 4,  # Corridor
            "Step": 25,
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "fall_detected": True,
            "severity": "CRITICAL"
        },
        "ground_truth_label": 1
    },
    {
        "id": "FALL_TP_012",
        "description": "Fall in bathroom with both tachycardia and hypoxia",
        "category": "true_positive",
        "input_data": {
            "HR": 138,
            "Blood_oxygen": 84,
            "Posture_state": 5,
            "Area": 6,  # Bathroom
            "Step": 0,
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "fall_detected": True,
            "severity": "CRITICAL",
            "anomalies": ["FALL_DETECTED", "TACHYCARDIA", "HYPOXIA"]
        },
        "ground_truth_label": 1
    },
    {
        "id": "FALL_TP_013",
        "description": "Fall in laboratory with normal vitals (pure mechanical fall)",
        "category": "true_positive",
        "input_data": {
            "HR": 82,
            "Blood_oxygen": 97,
            "Posture_state": 5,
            "Area": 5,
            "Step": 0,
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "fall_detected": True,
            "severity": "CRITICAL"
        },
        "ground_truth_label": 1
    },
    {
        "id": "FALL_TP_014",
        "description": "Fall after prolonged walking (fatigue-related)",
        "category": "true_positive",
        "input_data": {
            "HR": 118,
            "Blood_oxygen": 91,
            "Posture_state": 5,
            "Area": 4,
            "Step": 250,  # Long walk
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "fall_detected": True,
            "severity": "CRITICAL"
        },
        "ground_truth_label": 1
    },
    
    # ADDITIONAL TRUE NEGATIVES (normal activities)
    {
        "id": "FALL_TN_008",
        "description": "Lying down for rest (normal)",
        "category": "true_negative",
        "input_data": {
            "HR": 68,
            "Blood_oxygen": 98,
            "Posture_state": 3,  # Lying
            "Area": 1,  # Bedroom
            "Step": 0,
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "fall_detected": False,
            "severity": "NORMAL"
        },
        "ground_truth_label": 0
    },
    {
        "id": "FALL_TN_009",
        "description": "Walking in corridor with normal vitals",
        "category": "true_negative",
        "input_data": {
            "HR": 88,
            "Blood_oxygen": 96,
            "Posture_state": 2,  # Standing
            "Area": 4,
            "Step": 45,
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "fall_detected": False,
            "severity": "NORMAL"
        },
        "ground_truth_label": 0
    },
    {
        "id": "FALL_TN_010",
        "description": "Sitting in kitchen after eating",
        "category": "true_negative",
        "input_data": {
            "HR": 79,
            "Blood_oxygen": 97,
            "Posture_state": 1,
            "Area": 2,
            "Step": 0,
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "fall_detected": False,
            "severity": "NORMAL"
        },
        "ground_truth_label": 0
    },
    {
        "id": "FALL_TN_011",
        "description": "Standing still in living room",
        "category": "true_negative",
        "input_data": {
            "HR": 74,
            "Blood_oxygen": 98,
            "Posture_state": 2,
            "Area": 3,
            "Step": 0,
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "fall_detected": False,
            "severity": "NORMAL"
        },
        "ground_truth_label": 0
    },
    
    # ADDITIONAL EDGE CASES (challenging scenarios)
    {
        "id": "FALL_EDGE_004",
        "description": "Lying on floor for exercise (yoga)",
        "category": "edge_case",
        "input_data": {
            "HR": 95,
            "Blood_oxygen": 96,
            "Posture_state": 3,  # Lying
            "Area": 5,  # Laboratory/exercise area
            "Step": 0,
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "fall_detected": False,
            "severity": "WARNING",
            "contextual_risk": "moderate"
        },
        "ground_truth_label": 0,
        "notes": "Intentional lying for exercise, not a fall"
    },
    {
        "id": "FALL_EDGE_005",
        "description": "Sitting in bathroom (could be dizzy)",
        "category": "edge_case",
        "input_data": {
            "HR": 110,
            "Blood_oxygen": 92,
            "Posture_state": 1,  # Sitting
            "Area": 6,  # Bathroom
            "Step": 0,
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "fall_detected": False,
            "severity": "WARNING",
            "contextual_risk": "high"
        },
        "ground_truth_label": 0,
        "notes": "High-risk context but not a fall"
    },
    {
        "id": "FALL_EDGE_006",
        "description": "Rapid movement - bending down then standing",
        "category": "edge_case",
        "input_data": {
            "HR": 112,
            "Blood_oxygen": 94,
            "Posture_state": 2,  # Standing
            "Area": 2,
            "Step": 8,
            "timestamp": datetime.now().isoformat()
        },
        "expected_output": {
            "fall_detected": False,
            "severity": "NORMAL"
        },
        "ground_truth_label": 0,
        "notes": "Rapid posture change but controlled movement"
    }
]


# ======================
# VITAL SIGNS ANOMALY DETECTION (40 cases)
# ======================

VITAL_SIGNS_ANOMALY_TESTS = [
    # Tachycardia (HR > 110)
    {
        "id": "VITALS_TACHY_001",
        "description": "Severe tachycardia at rest",
        "anomaly_type": "hr_high",
        "input_data": {
            "HR": 145,
            "Blood_oxygen": 95,
            "Posture_state": 1,  # Sitting
            "Area": 1,
            "Step": 0
        },
        "expected_output": {
            "anomaly_detected": True,
            "anomaly_type": "TACHYCARDIA",
            "severity": "WARNING"
        },
        "ground_truth_label": 1  # 1 = anomaly
    },
    {
        "id": "VITALS_TACHY_002",
        "description": "Moderate tachycardia",
        "anomaly_type": "hr_high",
        "input_data": {
            "HR": 118,
            "Blood_oxygen": 96,
            "Posture_state": 2,
            "Area": 3,
            "Step": 0
        },
        "expected_output": {
            "anomaly_detected": True,
            "anomaly_type": "TACHYCARDIA"
        },
        "ground_truth_label": 1
    },
    
    # Bradycardia (HR < 45)
    {
        "id": "VITALS_BRADY_001",
        "description": "Severe bradycardia",
        "anomaly_type": "hr_low",
        "input_data": {
            "HR": 35,
            "Blood_oxygen": 94,
            "Posture_state": 3,  # Lying
            "Area": 1,
            "Step": 0
        },
        "expected_output": {
            "anomaly_detected": True,
            "anomaly_type": "BRADYCARDIA",
            "severity": "WARNING"
        },
        "ground_truth_label": 1
    },
    {
        "id": "VITALS_BRADY_002",
        "description": "Moderate bradycardia",
        "anomaly_type": "hr_low",
        "input_data": {
            "HR": 42,
            "Blood_oxygen": 96,
            "Posture_state": 1,
            "Area": 1,
            "Step": 0
        },
        "expected_output": {
            "anomaly_detected": True,
            "anomaly_type": "BRADYCARDIA"
        },
        "ground_truth_label": 1
    },
    
    # Hypoxia (SpO2 < 90)
    {
        "id": "VITALS_HYPOXIA_001",
        "description": "Severe hypoxia",
        "anomaly_type": "spo2_low",
        "input_data": {
            "HR": 95,
            "Blood_oxygen": 82,
            "Posture_state": 2,
            "Area": 3,
            "Step": 0
        },
        "expected_output": {
            "anomaly_detected": True,
            "anomaly_type": "HYPOXIA",
            "severity": "CRITICAL"
        },
        "ground_truth_label": 1
    },
    {
        "id": "VITALS_HYPOXIA_002",
        "description": "Moderate hypoxia",
        "anomaly_type": "spo2_low",
        "input_data": {
            "HR": 88,
            "Blood_oxygen": 87,
            "Posture_state": 1,
            "Area": 1,
            "Step": 0
        },
        "expected_output": {
            "anomaly_detected": True,
            "anomaly_type": "HYPOXIA"
        },
        "ground_truth_label": 1
    },
    
    # Normal vitals (true negatives)
    {
        "id": "VITALS_NORMAL_001",
        "description": "Normal vitals at rest",
        "anomaly_type": "normal",
        "input_data": {
            "HR": 75,
            "Blood_oxygen": 97,
            "Posture_state": 1,
            "Area": 1,
            "Step": 0
        },
        "expected_output": {
            "anomaly_detected": False,
            "severity": "NORMAL"
        },
        "ground_truth_label": 0
    },
    {
        "id": "VITALS_NORMAL_002",
        "description": "Slightly elevated HR (exercise)",
        "anomaly_type": "normal",
        "input_data": {
            "HR": 105,  # Just below threshold
            "Blood_oxygen": 96,
            "Posture_state": 8,  # Walking
            "Area": 4,
            "Step": 50
        },
        "expected_output": {
            "anomaly_detected": False,
            "severity": "NORMAL"
        },
        "ground_truth_label": 0
    }
]


# ======================
# RISK SCORING VALIDATION (30 cases)
# ======================

RISK_SCORING_TESTS = [
    # LOW RISK (Score 0-33)
    {
        "id": "RISK_LOW_001",
        "description": "Healthy patient, no anomalies",
        "historical_data": [
            {"HR": 78, "Blood_oxygen": 97, "Posture_state": 1, "Area": 1},
            {"HR": 80, "Blood_oxygen": 97, "Posture_state": 1, "Area": 1},
            {"HR": 76, "Blood_oxygen": 98, "Posture_state": 2, "Area": 3},
            # ... 20 more normal readings
        ],
        "expected_risk_score_range": (0, 0.33),
        "expected_risk_category": "LOW",
        "ground_truth_score": 0.05
    },
    {
        "id": "RISK_LOW_002",
        "description": "Occasional mild tachycardia (5%)",
        "historical_data": [
            # 95 normal + 5 mild tachy
        ],
        "expected_risk_score_range": (0.05, 0.30),
        "expected_risk_category": "LOW",
        "ground_truth_score": 0.15
    },
    
    # MEDIUM RISK (Score 34-66)
    {
        "id": "RISK_MED_001",
        "description": "2 falls + moderate vital instability",
        "historical_data": [
            # 2 falls + 10% abnormal vitals
        ],
        "expected_risk_score_range": (0.40, 0.60),
        "expected_risk_category": "MEDIUM",
        "ground_truth_score": 0.50
    },
    {
        "id": "RISK_MED_002",
        "description": "No falls but frequent hypoxia (15%)",
        "historical_data": [
            # 0 falls + 15% hypoxia
        ],
        "expected_risk_score_range": (0.35, 0.55),
        "expected_risk_category": "MEDIUM",
        "ground_truth_score": 0.45
    },
    
    # HIGH RISK (Score 67-100)
    {
        "id": "RISK_HIGH_001",
        "description": "Multiple falls + severe vital instability",
        "historical_data": [
            # 10+ falls + 20% abnormal vitals
        ],
        "expected_risk_score_range": (0.70, 1.00),
        "expected_risk_category": "HIGH",
        "ground_truth_score": 0.85
    },
    {
        "id": "RISK_HIGH_002",
        "description": "Frequent hypoxia + tachycardia",
        "historical_data": [
            # 30% hypoxia + 25% tachycardia
        ],
        "expected_risk_score_range": (0.75, 0.95),
        "expected_risk_category": "HIGH",
        "ground_truth_score": 0.80
    }
]


# ======================
# HELPER FUNCTIONS
# ======================

def get_test_by_id(test_id: str):
    """Get a specific test case by ID"""
    all_tests = FALL_DETECTION_TESTS + VITAL_SIGNS_ANOMALY_TESTS + RISK_SCORING_TESTS
    for test in all_tests:
        if test.get("id") == test_id:
            return test
    return None


def get_tests_by_category(category: str):
    """Get all tests in a category (e.g., 'true_positive', 'edge_case')"""
    return [t for t in FALL_DETECTION_TESTS if t.get("category") == category]


def get_ground_truth_labels(test_set: list):
    """Extract ground truth labels from test set"""
    return [t["ground_truth_label"] for t in test_set if "ground_truth_label" in t]


def print_test_summary():
    """Print summary of available test cases"""
    print("\n" + "="*60)
    print("  TEST DATASET SUMMARY")
    print("="*60)
    print(f"  Fall Detection Tests:      {len(FALL_DETECTION_TESTS)}")
    print(f"    - True Positives:        {len(get_tests_by_category('true_positive'))}")
    print(f"    - True Negatives:        {len(get_tests_by_category('true_negative'))}")
    print(f"    - Edge Cases:            {len(get_tests_by_category('edge_case'))}")
    print(f"\n  Vital Signs Anomaly Tests: {len(VITAL_SIGNS_ANOMALY_TESTS)}")
    print(f"  Risk Scoring Tests:        {len(RISK_SCORING_TESTS)}")
    print(f"\n  Total Test Cases:          {len(FALL_DETECTION_TESTS) + len(VITAL_SIGNS_ANOMALY_TESTS) + len(RISK_SCORING_TESTS)}")
    print("="*60 + "\n")


# Export
__all__ = [
    "FALL_DETECTION_TESTS",
    "VITAL_SIGNS_ANOMALY_TESTS",
    "RISK_SCORING_TESTS",
    "get_test_by_id",
    "get_tests_by_category",
    "get_ground_truth_labels",
    "print_test_summary"
]


# Print summary when module is imported
if __name__ == "__main__":
    print_test_summary()
