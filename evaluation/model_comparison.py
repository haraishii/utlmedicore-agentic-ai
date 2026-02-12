"""
Model Comparison Framework
===========================

Compare different LLM models for each agent role to find optimal configuration.

This script:
1. Tests multiple models (Ollama local + GPT cloud) for each agent
2. Measures accuracy, latency, token usage, and cost
3. Generates comparison report
4. Recommends best model per agent based on trade-offs

Usage:
    python evaluation/model_comparison.py --agent monitor --models "ollama:llama3.1:8b,openai:gpt-4o-mini"
"""

import argparse
import time
import pandas as pd
from typing import List, Dict, Any
import json

from opik import track
from evaluation.test_datasets import (
    FALL_DETECTION_TESTS,
    VITAL_SIGNS_ANOMALY_TESTS,
    get_tests_by_category,
    get_ground_truth_labels
)
from evaluation.metrics import (
    calculate_fall_detection_metrics,
    calculate_latency_metrics,
    calculate_token_cost,
    print_metrics_report
)
from evaluation.opik_integration import TrackedAISuiteClient


class ModelComparator:
    """
    Compare multiple LLM models for agent performance.
    """
    
    def __init__(self, agent_name: str,test_cases: List[Dict],):
        """
        Initialize model comparator.
        
        Args:
            agent_name: Name of agent ('monitor', 'analyzer', etc.)
            test_cases: List of test cases to run
        """
        self.agent_name = agent_name
        self.test_cases = test_cases
        self.ai_client = TrackedAISuiteClient()
        self.results = []
    
    def run_agent_with_model(
        self,
        model: str,
        test_case: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run agent logic with specific model on a test case.
        
        Args:
            model: Model name (e.g., "ollama:llama3.1:8b")
            test_case: Test case dict with input_data
        
        Returns:
            Agent output dict
        """
        input_data = test_case['input_data']
        
        # Build prompt based on agent type
        if self.agent_name == "monitor":
            prompt = self._build_monitor_prompt(input_data)
        elif self.agent_name == "analyzer":
            prompt = self._build_analyzer_prompt(input_data)
        elif self.agent_name == "predictor":
            prompt = self._build_predictor_prompt(input_data)
        else:
            prompt = f"Analyze this patient data: {json.dumps(input_data)}"
        
        # Call LLM
        start_time = time.time()
        
        response = self.ai_client.chat_completions_create(
            model=model,
            messages=[
                {"role": "system", "content": self._get_system_prompt()},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3
        )
        
        latency_ms = (time.time() - start_time) * 1000
        
        # Parse response
        output_text = response.choices[0].message.content
        
        # Extract structured output from LLM response
        try:
            # Try to parse as JSON if available
            if "{" in output_text and "}" in output_text:
                import re
                json_match = re.search(r'\{.*\}', output_text, re.DOTALL)
                if json_match:
                    parsed = json.loads(json_match.group())
                else:
                    parsed = self._parse_text_output(output_text)
            else:
                parsed = self._parse_text_output(output_text)
        except:
            parsed = self._parse_text_output(output_text)
        
        return {
            "output": parsed,
            "latency_ms": latency_ms,
            "response_text": output_text
        }
    
    def _build_monitor_prompt(self, data: Dict) -> str:
        """Build prompt for Monitor Agent"""
        return f"""Analyze this real-time patient sensor data for anomalies:

Heart Rate: {data.get('HR')} bpm
Blood Oxygen: {data.get('Blood_oxygen')}%
Posture State: {data.get('Posture_state')} (0=Unknown, 1=Sitting, 2=Standing, 3=Lying, 5=Fall, 8=Walking)
Location Area: {data.get('Area')}
Step Count: {data.get('Step')}

Detect any critical anomalies (falls, tachycardia, bradycardia, hypoxia) and classify severity.

Response format:
{{
    "fall_detected": true/false,
    "severity": "NORMAL/WARNING/CRITICAL",
    "anomalies": ["list", "of", "anomalies"]
}}"""
    
    def _build_analyzer_prompt(self, data: Dict) -> str:
        """Build prompt for Analyzer Agent"""
        return f"""Analyze patient activity patterns from this data:

{json.dumps(data, indent=2)}

Provide pattern analysis and risk assessment."""
    
    def _build_predictor_prompt(self, data: Dict) -> str:
        """Build prompt for Predictor Agent"""
        return f"""Predict future health risks based on this patient data:

{json.dumps(data, indent=2)}

Estimate next-hour risk and provide recommendations."""
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for the agent"""
        prompts = {
            "monitor": "You are a medical monitoring AI. Detect anomalies and classify severity accurately.",
            "analyzer": "You are a healthcare pattern analysis AI. Identify trends and calculate risk scores.",
            "predictor": "You are a predictive health AI. Forecast future risks and recommend interventions."
        }
        return prompts.get(self.agent_name, "You are a healthcare AI assistant.")
    
    def _parse_text_output(self, text: str) -> Dict:
        """Parse natural language output into structured format"""
        output = {
            "fall_detected": False,
            "severity": "NORMAL",
            "anomalies": []
        }
        
        text_lower = text.lower()
        
        # Detect fall
        if "fall" in text_lower and ("detected" in text_lower or "yes" in text_lower):
            output["fall_detected"] = True
        
        # Detect severity
        if "critical" in text_lower:
            output["severity"] = "CRITICAL"
        elif "warning" in text_lower or "moderate" in text_lower:
            output["severity"] = "WARNING"
        
        # Detect anomalies
        if "tachycardia" in text_lower:
            output["anomalies"].append("TACHYCARDIA")
        if "bradycardia" in text_lower:
            output["anomalies"].append("BRADYCARDIA")
        if "hypoxia" in text_lower:
            output["anomalies"].append("HYPOXIA")
        if "fall" in text_lower:
            output["anomalies"].append("FALL_DETECTED")
        
        return output
    
    def compare_models(self, models: List[str]) -> pd.DataFrame:
        """
        Compare multiple models on test cases.
        
        Args:
            models: List of model names to compare
        
        Returns:
            DataFrame with comparison results
        """
        results_list = []
        
        for model in models:
            print(f"\n{'='*60}")
            print(f"  Testing {self.agent_name.upper()} Agent with: {model}")
            print(f"{'='*60}")
            
            model_results = {
                "model": model,
                "agent": self.agent_name,
                "test_cases": len(self.test_cases),
                "predictions": [],
                "ground_truth": [],
                "latencies_ms": [],
                "success_count": 0,
                "error_count": 0
            }
            
            for i, test in enumerate(self.test_cases, 1):
                print(f"  [{i}/{len(self.test_cases)}] {test['id']}...", end=" ")
                
                try:
                    result = self.run_agent_with_model(model, test)
                    
                    # Extract prediction
                    prediction = 1 if result['output'].get('fall_detected', False) else 0
                    ground_truth = test.get('ground_truth_label', 0)
                    
                    model_results["predictions"].append(prediction)
                    model_results["ground_truth"].append(ground_truth)
                    model_results["latencies_ms"].append(result['latency_ms'])
                    model_results["success_count"] += 1
                    
                    print(f"[OK] {result['latency_ms']:.0f}ms")
                    
                except Exception as e:
                    model_results["error_count"] += 1
                    print(f"[FAIL] Error: {e}")
            
            # Calculate metrics
            if model_results["predictions"]:
                metrics = calculate_fall_detection_metrics(
                    model_results["predictions"],
                    model_results["ground_truth"]
                )
                latency_metrics = calculate_latency_metrics(model_results["latencies_ms"])
                
                # Estimate cost
                avg_tokens = 150  # Rough estimate
                total_cost = calculate_token_cost(
                    avg_tokens * len(self.test_cases),
                    avg_tokens * len(self.test_cases),
                    model
                )
                
                results_list.append({
                    "Model": model,
                    "Accuracy": metrics["accuracy"],
                    "Sensitivity": metrics["sensitivity"],
                    "Specificity": metrics["specificity"],
                    "F1 Score": metrics["f1_score"],
                    "Latency (mean)": latency_metrics["mean"],
                    "Latency (p95)": latency_metrics["p95"],
                    "Success Rate": model_results["success_count"] / len(self.test_cases),
                    "Total Cost": total_cost,
                    "Test Cases": len(self.test_cases)
                })
                
                print(f"\n  [RESULTS]:")
                print(f"     Accuracy:    {metrics['accuracy']:.3f}")
                print(f"     Sensitivity: {metrics['sensitivity']:.3f}")
                print(f"     Latency:     {latency_metrics['mean']:.0f}ms (mean), {latency_metrics['p95']:.0f}ms (p95)")
                print(f"     Cost:        ${total_cost:.4f}")
        
        # Create DataFrame
        df = pd.DataFrame(results_list)
        
        # Sort by F1 score (best overall metric)
        df = df.sort_values("F1 Score", ascending=False)
        
        return df
    
    def print_comparison_report(self, df: pd.DataFrame):
        """Print formatted comparison report"""
        print("\n" + "="*80)
        print(f"  MODEL COMPARISON REPORT - {self.agent_name.upper()} AGENT")
        print("="*80)
        print(df.to_string(index=False))
        print("="*80)
        
        # Recommendation
        best_model = df.iloc[0]["Model"]
        print(f"\n[WINNER] RECOMMENDED MODEL: {best_model}")
        print(f"   ├─ Accuracy: {df.iloc[0]['Accuracy']:.3f}")
        print(f"   ├─ F1 Score: {df.iloc[0]['F1 Score']:.3f}")
        print(f"   ├─ Latency:  {df.iloc[0]['Latency (mean)']:.0f}ms")
        print(f"   └─ Cost:     ${df.iloc[0]['Total Cost']:.4f}\n")
        
        # Trade-offs
        if len(df) > 1:
            print("[ANALYSIS] TRADE-OFF ANALYSIS:")
            fastest = df.loc[df["Latency (mean)"].idxmin()]
            cheapest = df.loc[df["Total Cost"].idxmin()]
            most_accurate = df.loc[df["F1 Score"].idxmax()]
            
            print(f"   Fastest:       {fastest['Model']} ({fastest['Latency (mean)']:.0f}ms)")
            print(f"   Cheapest:      {cheapest['Model']} (${cheapest['Total Cost']:.4f})")
            print(f"   Most Accurate: {most_accurate['Model']} (F1={most_accurate['F1 Score']:.3f})\n")


def main():
    """Main entry point for model comparison"""
    parser = argparse.ArgumentParser(description="Compare LLM models for agent performance")
    parser.add_argument(
        "--agent",
        type=str,
        required=True,
        choices=["monitor", "analyzer", "predictor", "alert", "coordinator"],
        help="Agent to test"
    )
    parser.add_argument(
        "--models",
        type=str,
        required=True,
        help="Comma-separated list of models (e.g., 'ollama:llama3.1:8b,openai:gpt-4o-mini')"
    )
    parser.add_argument(
        "--test-limit",
        type=int,
        default=None,
        help="Limit number of test cases (default: all)"
    )
    
    args = parser.parse_args()
    
    # Parse models
    models = [m.strip() for m in args.models.split(",")]
    
    # Get test cases (for Monitor agent, use fall detection tests)
    if args.agent == "monitor":
        test_cases = FALL_DETECTION_TESTS
    else:
        test_cases = VITAL_SIGNS_ANOMALY_TESTS
    
    # Limit test cases if specified
    if args.test_limit:
        test_cases = test_cases[:args.test_limit]
    
    # Run comparison
    comparator = ModelComparator(args.agent, test_cases)
    results_df = comparator.compare_models(models)
    
    # Print report
    comparator.print_comparison_report(results_df)
    
    # Save to CSV
    output_file = f"reports/model_comparison_{args.agent}_results.csv"
    results_df.to_csv(output_file, index=False)
    print(f"[SAVE] Results saved to: {output_file}\n")


if __name__ == "__main__":
    main()
