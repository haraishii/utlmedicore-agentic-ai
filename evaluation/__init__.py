# Opik Evaluation Framework for UTLMediCore
# This package provides performance tracking and evaluation for multi-agent system

__version__ = "1.0.0"

from .opik_integration import TrackedAISuiteClient, track_agent_call
from .metrics import (
    calculate_fall_detection_metrics,
    calculate_anomaly_detection_metrics,
    calculate_risk_scoring_metrics
)

__all__ = [
    "TrackedAISuiteClient",
    "track_agent_call",
    "calculate_fall_detection_metrics",
    "calculate_anomaly_detection_metrics",
    "calculate_risk_scoring_metrics"
]
