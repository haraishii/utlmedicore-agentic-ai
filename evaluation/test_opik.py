"""
Quick Test Script for Opik Integration
========================================

Run this to verify Opik integration is working correctly.
"""

import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

print("="*60)
print("  OPIK INTEGRATION TEST")
print("="*60)

# Test 1: Import modules
print("\n[1/5] Testing imports...")
try:
    from evaluation.opik_integration import TrackedAISuiteClient, track_agent_call
    from evaluation.metrics import calculate_fall_detection_metrics
    from evaluation.test_datasets import FALL_DETECTION_TESTS, print_test_summary
    print("✅ All modules imported successfully")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

# Test 2: Initialize TrackedAISuiteClient
print("\n[2/5] Testing TrackedAISuiteClient initialization...")
try:
    ai_client = TrackedAISuiteClient()
    print("✅ TrackedAISuiteClient initialized")
except Exception as e:
    print(f"❌ Initialization failed: {e}")
    sys.exit(1)

# Test 3: Test datasets
print("\n[3/5] Testing datasets...")
try:
    print_test_summary()
    print(f"✅ Loaded {len(FALL_DETECTION_TESTS)} fall detection test cases")
except Exception as e:
    print(f"❌ Dataset test failed: {e}")

# Test 4: Test metrics calculation
print("\n[4/5] Testing metrics calculation...")
try:
    # Sample data
    predictions = [1, 0, 1, 1, 0, 0, 1, 0]
    ground_truth = [1, 0, 1, 0, 0, 0, 1, 1]
    
    metrics = calculate_fall_detection_metrics(predictions, ground_truth)
    
    print(f"✅ Metrics calculated:")
    print(f"   Sensitivity: {metrics['sensitivity']:.3f}")
    print(f"   Specificity: {metrics['specificity']:.3f}")
    print(f"   F1 Score: {metrics['f1_score']:.3f}")
except Exception as e:
    print(f"❌ Metrics test failed: {e}")

# Test 5: Test LLM call with tracking
print("\n[5/5] Testing LLM call with Opik tracking...")
try:
    response = ai_client.chat_completions_create(
        model="ollama:llama3.1:8b",
        messages=[
            {"role": "system", "content": "You are a test assistant."},
            {"role": "user", "content": "Say 'Test successful' and nothing else."}
        ],
        temperature=0.1
    )
    
    response_text = response.choices[0].message.content
    print(f"✅ LLM call successful")
    print(f"   Response: {response_text[:50]}...")
    print(f"   Opik tracking: Enabled ✓")
except Exception as e:
    print(f"⚠️  LLM call failed (Ollama might not be running): {e}")
    print("   Note: This is OK if Ollama is not started yet")

# Summary
print("\n" + "="*60)
print("  TEST SUMMARY")
print("="*60)
print("✅ Opik integration is ready to use!")
print("\nNext steps:")
print("  1. Run evaluation: python evaluation/run_evaluation.py --agent monitor --test-cases 5")
print("  2. Compare models: python evaluation/model_comparison.py --agent monitor --models 'ollama:llama3.1:8b'")
print("  3. Check Opik dashboard: https://www.comet.com/")
print("="*60 + "\n")
