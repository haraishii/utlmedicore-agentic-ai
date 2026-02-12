"""
Healthcare-Specific Evaluation Metrics
=======================================

This module provides evaluation metrics tailored for healthcare monitoring:
- Fall detection metrics (sensitivity, specificity, PPV, NPV)
- Anomaly detection metrics (precision, recall, F1)
- Risk scoring metrics (MAE, RMSE, calibration)
- System performance metrics (latency, throughput)

All metrics follow clinical evaluation standards.
"""

from typing import List, Dict, Tuple, Any
import numpy as np
from sklearn.metrics import confusion_matrix, classification_report
import time


def calculate_fall_detection_metrics(
    predictions: List[int],
    ground_truth: List[int]
) -> Dict[str, float]:
    """
    Calculate fall detection performance metrics.
    
    Metrics calculated:
    - Sensitivity (True Positive Rate, Recall): TP / (TP + FN)
    - Specificity (True Negative Rate): TN / (TN + FP)
    - Precision (Positive Predictive Value): TP / (TP + FP)
    - NPV (Negative Predictive Value): TN / (TN + FN)
    - F1 Score: Harmonic mean of precision and recall
    - Accuracy: (TP + TN) / Total
    - False Positive Rate: FP / (FP + TN)
    - False Negative Rate: FN / (FN + TP)
    
    Args:
        predictions: List of predicted fall events (1=fall, 0=no fall)
        ground_truth: List of actual fall events (1=fall, 0=no fall)
    
    Returns:
        Dictionary with all metrics
    
    Example:
        predictions = [1, 0, 1, 0, 1, 1, 0, 0]
        ground_truth = [1, 0, 1, 0, 0, 1, 0, 1]
        
        metrics = calculate_fall_detection_metrics(predictions, ground_truth)
        # {'sensitivity': 0.75, 'specificity': 1.0, ...}
    """
    if len(predictions) != len(ground_truth):
        raise ValueError("Predictions and ground truth must have same length")
    
    if len(predictions) == 0:
        return {
            "sensitivity": 0.0,
            "specificity": 0.0,
            "precision": 0.0,
            "npv": 0.0,
            "f1_score": 0.0,
            "accuracy": 0.0,
            "false_positive_rate": 0.0,
            "false_negative_rate": 0.0,
            "true_positives": 0,
            "true_negatives": 0,
            "false_positives": 0,
            "false_negatives": 0,
            "total_samples": 0
        }
    
    # Calculate confusion matrix
    tn, fp, fn, tp = confusion_matrix(ground_truth, predictions, labels=[0, 1]).ravel()
    
    # Calculate metrics with zero-division handling
    sensitivity = tp / (tp + fn) if (tp + fn) > 0 else 0.0
    specificity = tn / (tn + fp) if (tn + fp) > 0 else 0.0
    precision = tp / (tp + fp) if (tp + fp) > 0 else 0.0
    npv = tn / (tn + fn) if (tn + fn) > 0 else 0.0
    
    f1 = (2 * precision * sensitivity) / (precision + sensitivity) if (precision + sensitivity) > 0 else 0.0
    accuracy = (tp + tn) / (tp + tn + fp + fn)
    
    fpr = fp / (fp + tn) if (fp + tn) > 0 else 0.0
    fnr = fn / (fn + tp) if (fn + tp) > 0 else 0.0
    
    return {
        "sensitivity": round(sensitivity, 4),  # Recall, TPR
        "specificity": round(specificity, 4),  # TNR
        "precision": round(precision, 4),      # PPV
        "npv": round(npv, 4),                  # Negative Predictive Value
        "f1_score": round(f1, 4),
        "accuracy": round(accuracy, 4),
        "false_positive_rate": round(fpr, 4),
        "false_negative_rate": round(fnr, 4),
        "true_positives": int(tp),
        "true_negatives": int(tn),
        "false_positives": int(fp),
        "false_negatives": int(fn),
        "total_samples": len(predictions)
    }


def calculate_anomaly_detection_metrics(
    predictions: List[int],
    ground_truth: List[int],
    anomaly_type: str = "general"
) -> Dict[str, float]:
    """
    Calculate metrics for vital signs anomaly detection.
    
    This function calculates precision/recall for detecting abnormal
    vital signs (e.g., tachycardia, bradycardia, hypoxia).
    
    Args:
        predictions: Predicted anomalies (1=anomaly, 0=normal)
        ground_truth: Actual anomalies (1=anomaly, 0=normal)
        anomaly_type: Type of anomaly ("hr_high", "hr_low", "hypoxia", "general")
    
    Returns:
        Dictionary with precision, recall, F1, etc.
    
    Example:
        # Detecting tachycardia (HR > 110)
        predictions = [1, 0, 1, 1, 0, 0]
        ground_truth = [1, 0, 1, 0, 0, 1]
        
        metrics = calculate_anomaly_detection_metrics(
            predictions, ground_truth, anomaly_type="hr_high"
        )
    """
    metrics = calculate_fall_detection_metrics(predictions, ground_truth)
    
    # Add anomaly-specific metadata
    metrics["anomaly_type"] = anomaly_type
    
    # Rename metrics for anomaly detection context
    metrics["recall"] = metrics["sensitivity"]  # Same as sensitivity
    
    return metrics


def calculate_risk_scoring_metrics(
    predicted_scores: List[float],
    actual_scores: List[float],
    predicted_categories: List[str] = None,
    actual_categories: List[str] = None
) -> Dict[str, float]:
    """
    Calculate metrics for risk score predictions.
    
    Metrics:
    - MAE (Mean Absolute Error): Average absolute difference
    - RMSE (Root Mean Square Error): Square root of MSE
    - Correlation: Pearson correlation coefficient
    - Category Accuracy: % of correct LOW/MEDIUM/HIGH classifications
    
    Args:
        predicted_scores: Predicted risk scores (0-1 or 0-100)
        actual_scores: Actual risk scores
        predicted_categories: Optional LOW/MEDIUM/HIGH categories
        actual_categories: Optional actual categories
    
    Returns:
        Dictionary with regression and classification metrics
    
    Example:
        predicted = [0.2, 0.5, 0.8, 0.3]
        actual = [0.3, 0.6, 0.75, 0.4]
        
        metrics = calculate_risk_scoring_metrics(predicted, actual)
        # {'mae': 0.1, 'rmse': 0.11, ...}
    """
    if len(predicted_scores) != len(actual_scores):
        raise ValueError("Predicted and actual must have same length")
    
    # Convert to numpy arrays
    pred = np.array(predicted_scores)
    actual = np.array(actual_scores)
    
    # Calculate regression metrics
    mae = np.mean(np.abs(pred - actual))
    mse = np.mean((pred - actual) ** 2)
    rmse = np.sqrt(mse)
    
    # Correlation
    correlation = np.abs(corrcoef(pred, actual)[0, 1]) if len(pred) > 1 else 0.0
    
    metrics = {
        "mae": round(float(mae), 4),
        "rmse": round(float(rmse), 4),
        "mse": round(float(mse), 4),
        "correlation": round(float(correlation), 4),
        "mean_predicted": round(float(np.mean(pred)), 4),
        "mean_actual": round(float(np.mean(actual)), 4),
        "std_predicted": round(float(np.std(pred)), 4),
        "std_actual": round(float(np.std(actual)), 4)
    }
    
    # Calculate category accuracy if provided
    if predicted_categories and actual_categories:
        if len(predicted_categories) != len(actual_categories):
            raise ValueError("Category lists must have same length")
        
        correct = sum(p == a for p, a in zip(predicted_categories, actual_categories))
        category_accuracy = correct / len(predicted_categories)
        
        metrics["category_accuracy"] = round(category_accuracy, 4)
        metrics["category_errors"] = len(predicted_categories) - correct
    
    return metrics


def calculate_latency_metrics(
    latencies_ms: List[float],
    percentiles: List[int] = [50, 90, 95, 99]
) -> Dict[str, float]:
    """
    Calculate latency distribution metrics.
    
    Args:
        latencies_ms: List of latency measurements in milliseconds
        percentiles: Percentiles to calculate (default: [50, 90, 95, 99])
    
    Returns:
        Dictionary with mean, median, percentiles, min, max
    
    Example:
        latencies = [450, 520, 380, 600, 490, 510]
        metrics = calculate_latency_metrics(latencies)
        # {'mean': 491.67, 'p50': 495, 'p95': 590, ...}
    """
    if not latencies_ms:
        return {
            "mean": 0.0,
            "median": 0.0,
            "min": 0.0,
            "max": 0.0,
            "std": 0.0,
            "count": 0
        }
    
    latencies = np.array(latencies_ms)
    
    metrics = {
        "mean": round(float(np.mean(latencies)), 2),
        "median": round(float(np.median(latencies)), 2),
        "min": round(float(np.min(latencies)), 2),
        "max": round(float(np.max(latencies)), 2),
        "std": round(float(np.std(latencies)), 2),
        "count": len(latencies)
    }
    
    # Calculate percentiles
    for p in percentiles:
        metrics[f"p{p}"] = round(float(np.percentile(latencies, p)), 2)
    
    return metrics


def calculate_token_cost(
    input_tokens: int,
    output_tokens: int,
    model: str
) -> float:
    """
    Estimate cost for LLM API calls.
    
    Pricing (as of 2026):
    - GPT-4o: $5/1M input, $15/1M output
    - GPT-4o-mini: $0.15/1M input, $0.60/1M output
    - Ollama (local): $0 (free)
    
    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        model: Model name (e.g., "openai:gpt-4o", "ollama:llama3.1:8b")
    
    Returns:
        Estimated cost in USD
    
    Example:
        cost = calculate_token_cost(1000, 500, "openai:gpt-4o")
        # Returns: 0.0125 ($0.0125)
    """
    # Pricing per 1M tokens (input, output)
    pricing = {
        "gpt-4o": (5.0, 15.0),
        "gpt-4o-mini": (0.15, 0.60),
        "gpt-4-turbo": (10.0, 30.0),
        "gpt-3.5-turbo": (0.50, 1.50),
        # All Ollama models are free (local)
        "ollama": (0.0, 0.0)
    }
    
    # Determine model type
    model_lower = model.lower()
    
    if "ollama:" in model_lower:
        input_price, output_price = pricing["ollama"]
    elif "gpt-4o-mini" in model_lower:
        input_price, output_price = pricing["gpt-4o-mini"]
    elif "gpt-4o" in model_lower:
        input_price, output_price = pricing["gpt-4o"]
    elif "gpt-4" in model_lower:
        input_price, output_price = pricing["gpt-4-turbo"]
    elif "gpt-3.5" in model_lower:
        input_price, output_price = pricing["gpt-3.5-turbo"]
    else:
        # Default: assume free (local model)
        input_price, output_price = (0.0, 0.0)
    
    # Calculate cost
    input_cost = (input_tokens / 1_000_000) * input_price
    output_cost = (output_tokens / 1_000_000) * output_price
    total_cost = input_cost + output_cost
    
    return round(total_cost, 6)


def calculate_agent_agreement_rate(
    agent_outputs: List[Dict[str, Any]],
    key_to_compare: str = "severity"
) -> Dict[str, float]:
    """
    Calculate agreement rate between multiple agent runs.
    
    Useful for:
    - Testing consistency of same agent across runs
    - Comparing different models for same agent
    - Detecting non-deterministic behavior
    
    Args:
        agent_outputs: List of agent output dicts
        key_to_compare: Which key to compare agreement on
    
    Returns:
        Dictionary with agreement metrics
    
    Example:
        outputs = [
            {"severity": "CRITICAL", "risk": 0.8},
            {"severity": "CRITICAL", "risk": 0.85},
            {"severity": "WARNING", "risk": 0.6}
        ]
        
        metrics = calculate_agent_agreement_rate(outputs, "severity")
        # {'agreement_rate': 0.667, 'mode_value': 'CRITICAL', ...}
    """
    if not agent_outputs:
        return {"agreement_rate": 0.0, "sample_count": 0}
    
    # Extract values for the key
    values = [output.get(key_to_compare) for output in agent_outputs if key_to_compare in output]
    
    if not values:
        return {"agreement_rate": 0.0, "sample_count": 0, "error": f"Key '{key_to_compare}' not found"}
    
    # Find mode (most common value)
    from collections import Counter
    value_counts = Counter(values)
    mode_value, mode_count = value_counts.most_common(1)[0]
    
    agreement_rate = mode_count / len(values)
    
    return {
        "agreement_rate": round(agreement_rate, 4),
        "mode_value": mode_value,
        "mode_count": mode_count,
        "unique_values": len(value_counts),
        "sample_count": len(values),
        "value_distribution": dict(value_counts)
    }


def print_metrics_report(metrics: Dict[str, Any], title: str = "Metrics Report"):
    """
    Pretty print metrics in a readable format.
    
    Args:
        metrics: Dictionary of metrics
        title: Report title
    
    Example:
        metrics = calculate_fall_detection_metrics(pred, truth)
        print_metrics_report(metrics, "Fall Detection Performance")
    """
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")
    
    for key, value in metrics.items():
        if isinstance(value, float):
            print(f"  {key:30s}: {value:.4f}")
        elif isinstance(value, dict):
            print(f"  {key}:")
            for k, v in value.items():
                print(f"    {k:26s}: {v}")
        else:
            print(f"  {key:30s}: {value}")
    
    print(f"{'='*60}\n")


# Helper function for correlation
def corrcoef(x, y):
    """Calculate Pearson correlation coefficient"""
    return np.corrcoef(x, y)


# Export all metrics functions
__all__ = [
    "calculate_fall_detection_metrics",
    "calculate_anomaly_detection_metrics",
    "calculate_risk_scoring_metrics",
    "calculate_latency_metrics",
    "calculate_token_cost",
    "calculate_agent_agreement_rate",
    "print_metrics_report"
]
