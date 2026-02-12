"""
Main Evaluation Runner
======================

Run comprehensive evaluation of all agents with Opik tracking.

This script:
1. Loads test datasets
2. Runs each agent on test cases
3. Calculates metrics (sensitivity, specificity, etc.)
4. Logs results to Opik dashboard
5. Generates evaluation report

Usage:
    # Evaluate Monitor Agent
    python evaluation/run_evaluation.py --agent monitor --test-cases 10
    
    # Evaluate all agents
    python evaluation/run_evaluation.py --all --test-cases 20
    
    # Compare models
    python evaluation/run_evaluation.py --agent monitor --compare-models
"""

import argparse
import sys
import os
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from evaluation.test_datasets import (
    FALL_DETECTION_TESTS,
    VITAL_SIGNS_ANOMALY_TESTS,
    get_tests_by_category,
    print_test_summary
)
from evaluation.metrics import (
    calculate_fall_detection_metrics,
    calculate_latency_metrics,
    print_metrics_report
)
from evaluation.opik_integration import (
    TrackedAISuiteClient,
    log_evaluation_metric
)
from evaluation.model_comparison import ModelComparator


def evaluate_monitor_agent(test_cases, limit=None):
    """
    Evaluate Monitor Agent on fall detection test cases.
    
    Args:
        test_cases: List of test cases
        limit: Maximum number of test cases to run
    
    Returns:
        Dictionary with evaluation results
    """
    print("\n" + "="*60)
    print("  EVALUATING MONITOR AGENT")
    print("="*60)
    
    # Limit test cases
    if limit:
        test_cases = test_cases[:limit]
    
    ai_client = TrackedAISuiteClient()
    model = "ollama:llama3.1:8b"  # Default model
    
    predictions = []
    ground_truth = []
    latencies = []
    
    for i, test in enumerate(test_cases, 1):
        print(f"[{i}/{len(test_cases)}] Testing {test['id']}...", end=" ")
        
        try:
            import time
            start = time.time()
            
            # Build prompt
            prompt = f"""Analyze this patient sensor data for fall detection:

Heart Rate: {test['input_data']['HR']} bpm
Blood Oxygen: {test['input_data']['Blood_oxygen']}%
Posture State: {test['input_data']['Posture_state']}
Location: Area {test['input_data']['Area']}

Is this a fall? (Posture_state=5 indicates fall)
Respond with YES or NO and severity level."""
            
            # Call LLM
            response = ai_client.chat_completions_create(
                model=model,
                messages=[
                    {"role": "system", "content": "You are a fall detection AI. Analyze medical data accurately."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            latency = (time.time() - start) * 1000
            
            # Parse response
            response_text = response.choices[0].message.content.lower()
            fall_detected = "yes" in response_text or "fall" in response_text
            
            # Record prediction
            prediction = 1 if fall_detected else 0
            truth = test['ground_truth_label']
            
            predictions.append(prediction)
            ground_truth.append(truth)
            latencies.append(latency)
            
            # Log to Opik
            log_evaluation_metric(
                f"fall_detection_case_{test['id']}",
                1.0 if prediction == truth else 0.0,
                agent_name="Monitor",
                tags=["fall_detection", "evaluation"]
            )
            
            status = "[OK]" if prediction == truth else "[FAIL]"
            print(f"{status} {latency:.0f}ms (pred={prediction}, truth={truth})")
            
        except Exception as e:
            print(f"[FAIL] Error: {e}")
    
    # Calculate metrics
    metrics = calculate_fall_detection_metrics(predictions, ground_truth)
    latency_metrics = calculate_latency_metrics(latencies)
    
    # Print results
    print_metrics_report(metrics, "Monitor Agent - Fall Detection Metrics")
    print_metrics_report(latency_metrics, "Monitor Agent - Latency Metrics")
    
    # Log summary metrics to Opik
    log_evaluation_metric("monitor_sensitivity", metrics["sensitivity"], "Monitor")
    log_evaluation_metric("monitor_specificity", metrics["specificity"], "Monitor")
    log_evaluation_metric("monitor_f1_score", metrics["f1_score"], "Monitor")
    log_evaluation_metric("monitor_avg_latency", latency_metrics["mean"], "Monitor")
    
    return {
        "agent": "Monitor",
        "model": model,
        "test_cases": len(test_cases),
        "metrics": metrics,
        "latency": latency_metrics
    }


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Run agent evaluation with Opik tracking")
    parser.add_argument(
        "--agent",
        type=str,
        choices=["monitor", "analyzer", "predictor", "alert", "coordinator", "all"],
        default="monitor",
        help="Agent to evaluate (default: monitor)"
    )
    parser.add_argument(
        "--test-cases",
        type=int,
        default=10,
        help="Number of test cases to run (default: 10)"
    )
    parser.add_argument(
        "--compare-models",
        action="store_true",
        help="Run model comparison (Ollama vs GPT)"
    )
    parser.add_argument(
        "--show-tests",
        action="store_true",
        help="Show test dataset summary"
    )
    
    args = parser.parse_args()
    
    # Show test summary
    if args.show_tests:
        print_test_summary()
        return
    
    # Run model comparison
    if args.compare_models:
        print("\n[COMPARE] Running Model Comparison...")
        comparator = ModelComparator(
            agent_name=args.agent,
            test_cases=FALL_DETECTION_TESTS[:args.test_cases]
        )
        
        models = [
            "ollama:llama3.1:8b",
            "ollama:medllama2:7b",
            # Add GPT if you have API key
            # "openai:gpt-4o-mini"
        ]
        
        results_df = comparator.compare_models(models)
        comparator.print_comparison_report(results_df)
        return
    
    # Run evaluation
    print(f"\n{'='*60}")
    print(f"  OPIK EVALUATION - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}")
    print(f"  Agent:       {args.agent}")
    print(f"  Test Cases:  {args.test_cases}")
    print(f"  Opik:        Enabled")
    print(f"{'='*60}\n")
    
    if args.agent == "monitor" or args.agent == "all":
        results = evaluate_monitor_agent(
            FALL_DETECTION_TESTS,
            limit=args.test_cases
        )
        
        print("\n[DONE] Evaluation complete!")
        print(f"[INFO] Check Opik dashboard: https://www.comet.com/")
        print(f"       Workspace: utlmedicore")
    
    if args.agent == "all":
        print("\n[WARN] Other agents (Analyzer, Predictor) not yet implemented.")
        print("    Implement similar to evaluate_monitor_agent()")


if __name__ == "__main__":
    main()
