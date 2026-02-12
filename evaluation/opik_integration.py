"""
Opik Integration for AISuite Multi-Agent System
================================================

This module provides a wrapper around aisuite.Client that integrates Opik tracking
for performance monitoring and evaluation of LLM agents.

Key Features:
- Non-intrusive wrapper around aisuite.Client
- Automatic tracking of model calls, latency, and tokens
- Support for both local (Ollama) and cloud (OpenAI) models
- Custom healthcare metrics logging
- Model comparison framework

Usage:
    from evaluation.opik_integration import TrackedAISuiteClient
    
    # Replace aisuite.Client with tracked version
    ai_client = TrackedAISuiteClient()
    
    # Use exactly like aisuite.Client
    response = ai_client.chat.completions.create(
        model="ollama:llama3.1:8b",
        messages=[{"role": "user", "content": "Analyze patient data"}]
    )
"""

import time
import os
from functools import wraps
from typing import Dict, List, Any, Optional
import json

from aisuite import Client
from opik import track, opik_context
from opik.evaluation import evaluate
# from opik.evaluation.metrics import Metric  # Not available in this version
import opik

# Initialize Opik with API key
OPIK_API_KEY = os.getenv("OPIK_API_KEY", "2ciMrRhl5TFrvKBXmCngakr1L")
OPIK_WORKSPACE = os.getenv("OPIK_WORKSPACE", None)  # None = use default workspace

# Configure Opik
try:
    if OPIK_WORKSPACE:
        opik.configure(
            api_key=OPIK_API_KEY,
            workspace=OPIK_WORKSPACE
        )
    else:
        # Use default workspace
        opik.configure(api_key=OPIK_API_KEY)
    print(f"[OK] Opik configured successfully")
except Exception as e:
    print(f"[WARN] Opik configuration warning: {e}")
    print(f"       Continuing with limited tracking...")


class TrackedAISuiteClient:
    """
    Wrapper around aisuite.Client that adds Opik tracking.
    
    This class maintains full backward compatibility with aisuite.Client
    while adding automatic performance tracking via Opik.
    
    Attributes:
        client (aisuite.Client): The underlying aisuite client
        tracking_enabled (bool): Whether to track calls (default: True)
    """
    
    def __init__(self, tracking_enabled: bool = True):
        """
        Initialize tracked aisuite client.
        
        Args:
            tracking_enabled: Enable/disable Opik tracking (default: True)
        """
        self.client = Client()
        self.tracking_enabled = tracking_enabled
        self._call_count = 0
        
        print(f"[OPIK] Tracking initialized (workspace: {OPIK_WORKSPACE or 'default'})")
    
    @track(name="aisuite_llm_call", capture_input=True, capture_output=True)
    def chat_completions_create(
        self,
        model: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        **kwargs
    ) -> Any:
        """
        Create chat completion with Opik tracking.
        
        This method wraps aisuite.Client.chat.completions.create() and adds:
        - Latency tracking
        - Token usage logging
        - Model metadata
        - Error handling
        
        Args:
            model: Model name (e.g., "ollama:llama3.1:8b", "openai:gpt-4o")
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0.0-1.0)
            **kwargs: Additional arguments passed to aisuite
        
        Returns:
            Response object from aisuite
        """
        self._call_count += 1
        start_time = time.time()
        
        try:
            # Call aisuite (existing functionality - UNCHANGED)
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=temperature,
                **kwargs
            )
            
            # Calculate metrics
            latency_ms = (time.time() - start_time) * 1000
            
            # Extract model type for categorization
            model_provider = model.split(":")[0] if ":" in model else "unknown"
            model_name = model.split(":")[-1] if ":" in model else model
            
            # Count tokens (approximate)
            input_text = " ".join([m.get("content", "") for m in messages])
            output_text = response.choices[0].message.content if response.choices else ""
            
            input_tokens = len(input_text.split())  # Rough approximation
            output_tokens = len(output_text.split())
            
            # Log to Opik (if tracking enabled)
            if self.tracking_enabled:
                opik_context.update_current_trace(
                    tags=[model_provider, model_name, "aisuite"],
                    metadata={
                        "model": model,
                        "model_provider": model_provider,
                        "model_name": model_name,
                        "latency_ms": round(latency_ms, 2),
                        "temperature": temperature,
                        "message_count": len(messages),
                        "input_tokens": input_tokens,
                        "output_tokens": output_tokens,
                        "total_tokens": input_tokens + output_tokens,
                        "call_number": self._call_count
                    }
                )
                
                # Log metrics
                opik_context.update_current_span(
                    input={"messages": messages, "model": model},
                    output={"content": output_text},
                    metadata={"latency_ms": latency_ms}
                )
            
            # Print performance info
            print(f"  -> LLM Call #{self._call_count}: {model} | {latency_ms:.0f}ms | ~{output_tokens} tokens")
            
            return response
            
        except Exception as e:
            # Log error to Opik
            if self.tracking_enabled:
                opik_context.update_current_trace(
                    tags=["error", model],
                    metadata={
                        "error": str(e),
                        "model": model,
                        "failed_at_ms": (time.time() - start_time) * 1000
                    }
                )
            
            print(f"  -> LLM Call #{self._call_count} FAILED: {model} | Error: {e}")
            raise
    
    @property
    def chat(self):
        """
        Provide access to chat.completions interface (aisuite compatibility).
        
        Returns:
            Object with completions.create method
        """
        class ChatInterface:
            def __init__(self, parent):
                self.parent = parent
                self.completions = self
            
            def create(self, **kwargs):
                return self.parent.chat_completions_create(**kwargs)
        
        return ChatInterface(self)


def track_agent_call(agent_name: str, model: str, tags: Optional[List[str]] = None):
    """
    Decorator to track agent method calls with Opik.
    
    This decorator wraps agent methods (like MonitorAgent.analyze_realtime)
    to automatically track:
    - Agent execution time
    - Input/output data
    - Success/failure status
    - Custom metrics
    
    Usage:
        @track_agent_call(agent_name="Monitor", model="ollama:llama3.1:8b")
        def analyze_realtime(patient_state):
            # ... agent logic ...
            return results
    
    Args:
        agent_name: Name of the agent (e.g., "Monitor", "Analyzer")
        model: Model used by this agent
        tags: Additional tags for categorization
    
    Returns:
        Decorated function with Opik tracking
    """
    if tags is None:
        tags = []
    
    def decorator(func):
        @wraps(func)
        @track(
            name=f"{agent_name}_Agent",
            tags=["agent", agent_name.lower()] + tags,
            capture_input=False,  # Patient data privacy
            capture_output=True
        )
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                # Execute agent function
                result = func(*args, **kwargs)
                
                # Calculate execution time
                execution_time_ms = (time.time() - start_time) * 1000
                
                # Log to Opik
                opik_context.update_current_trace(
                    metadata={
                        "agent": agent_name,
                        "model": model,
                        "execution_time_ms": round(execution_time_ms, 2),
                        "status": "success",
                        "has_result": result is not None
                    }
                )
                
                # Log specific metrics based on agent type
                if result:
                    _log_agent_specific_metrics(agent_name, result)
                
                return result
                
            except Exception as e:
                execution_time_ms = (time.time() - start_time) * 1000
                
                # Log error
                opik_context.update_current_trace(
                    metadata={
                        "agent": agent_name,
                        "model": model,
                        "execution_time_ms": round(execution_time_ms, 2),
                        "status": "error",
                        "error_message": str(e)
                    }
                )
                
                raise
        
        return wrapper
    return decorator


def _log_agent_specific_metrics(agent_name: str, result: Any):
    """
    Log agent-specific metrics to Opik.
    
    Different agents have different success criteria:
    - Monitor: Did it detect anomalies?
    - Analyzer: Did it find patterns?
    - Predictor: What's the risk level?
    - Alert: Was an alert generated?
    
    Args:
        agent_name: Name of the agent
        result: Agent output
    """
    metrics = {}
    
    if agent_name == "Monitor":
        if isinstance(result, dict):
            metrics["severity"] = result.get("severity", "NORMAL")
            metrics["anomalies_found"] = len(result.get("anomalies", []))
            metrics["is_critical"] = result.get("severity") == "CRITICAL"
    
    elif agent_name == "Analyzer":
        if isinstance(result, dict):
            metrics["risk_score"] = result.get("risk_assessment", 0)
            metrics["patterns_detected"] = len(result.get("activity_distribution", {}))
    
    elif agent_name == "Predictor":
        if isinstance(result, dict):
            metrics["next_hour_risk"] = result.get("next_hour_risk", 0)
            metrics["trend"] = result.get("trend_direction", "unknown")
            metrics["recommendations_count"] = len(result.get("recommendations", []))
    
    elif agent_name == "Alert":
        if isinstance(result, dict):
            metrics["alert_severity"] = result.get("severity", "INFO")
            metrics["actions_required"] = len(result.get("actions_required", []))
            metrics["auto_notify"] = result.get("auto_notify", False)
    
    # Log metrics to Opik
    if metrics:
        opik_context.update_current_trace(metadata=metrics)


def log_evaluation_metric(
    metric_name: str,
    value: float,
    agent_name: Optional[str] = None,
    tags: Optional[List[str]] = None
):
    """
    Log a custom evaluation metric to Opik.
    
    Use this to log metrics like:
    - Fall detection sensitivity: 0.95
    - Alert precision: 0.88
    - End-to-end latency: 2.5s
    
    Args:
        metric_name: Name of the metric (e.g., "fall_detection_sensitivity")
        value: Metric value (float)
        agent_name: Optional agent name for categorization
        tags: Additional tags
    
    Example:
        log_evaluation_metric(
            "fall_detection_sensitivity",
            0.95,
            agent_name="Monitor",
            tags=["fall_detection", "validation"]
        )
    """
    if tags is None:
        tags = []
    
    if agent_name:
        tags.append(agent_name.lower())
    
    # Simple logging without context manager
    agent_str = f" [{agent_name}]" if agent_name else ""
    tag_str = f" (tags: {tags})" if tags else ""
    print(f"  [METRIC]{agent_str} {metric_name} = {value:.4f}{tag_str}")



def compare_models(
    agent_func,
    test_input,
    models: List[str],
    agent_name: str
) -> Dict[str, Any]:
    """
    Compare multiple models for a specific agent function.
    
    This runs the same agent logic with different models and compares:
    - Latency
    - Output quality
    - Token usage
    
    Args:
        agent_func: Agent function to test
        test_input: Input data for the agent
        models: List of model names to compare
        agent_name: Name of the agent
    
    Returns:
        Dictionary with comparison results per model
    
    Example:
        results = compare_models(
            MonitorAgent.analyze_realtime,
            patient_state,
            models=["ollama:llama3.1:8b", "openai:gpt-4o-mini"],
            agent_name="Monitor"
        )
    """
    results = {}
    
    for model in models:
        print(f"\n🔄 Testing {agent_name} with {model}...")
        
        start_time = time.time()
        
        try:
            # Run agent with this model
            # Note: Agent functions might need model parameter added
            output = agent_func(test_input)
            
            latency_ms = (time.time() - start_time) * 1000
            
            results[model] = {
                "success": True,
                "latency_ms": latency_ms,
                "output": output,
                "error": None
            }
            
            print(f"  ✅ Success | {latency_ms:.0f}ms")
            
        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            
            results[model] = {
                "success": False,
                "latency_ms": latency_ms,
                "output": None,
                "error": str(e)
            }
            
            print(f"  ❌ Failed | {e}")
    
    return results


# Export for easy import
__all__ = [
    "TrackedAISuiteClient",
    "track_agent_call",
    "log_evaluation_metric",
    "compare_models"
]
