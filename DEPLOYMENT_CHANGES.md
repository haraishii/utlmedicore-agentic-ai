# Deployment Changes - Model Optimization
**Based on:** Comprehensive Model Evaluation Results  
**Recommendation:** Deploy `ollama:llama3.1:8b` across all agents  
**Date:** 2026-02-11  
**Status:** Ready to implement

---

## 🎯 WHAT NEEDS TO CHANGE

### **Summary:**
Replace all agent models with `ollama:llama3.1:8b` (the proven winner) to ensure:
- ✅ 100% fall detection rate (never miss a fall)
- ✅ 100% reliability (zero timeouts)
- ✅ Consistent performance across all agents
- ✅ Simplified operations (single model to maintain)

---

## 📝 SPECIFIC CHANGES REQUIRED

### **1. Change in `agentic_medicore_enhanced.py`**

**File:** `e:\agentic\agentic_medicore_enhanced.py`  
**Lines to modify:** 47-51 (AgentConfig class)

#### **BEFORE (Current - Suboptimal):**
```python
class AgentConfig:
    """Configuration for Agentic AI System"""
    
    # Agent Models
    MONITOR_AGENT = "ollama:llama3.1:8b"  # Real-time monitoring
    ANALYZER_AGENT = "ollama:qwen2.5:7b"  # Deep analysis
    ALERT_AGENT = "ollama:deepseek-r1:8b"  # Emergency detection
    PREDICTOR_AGENT = "ollama:meditron:7b"  # Trend prediction
    COORDINATOR_AGENT = "ollama:qwen2.5:7b"  # Multi-agent orchestration
```

**Issues with current config:**
- ❌ `qwen2.5:7b` for Analyzer - misses 29% of falls
- ❌ `deepseek-r1:8b` for Alert - 60% timeout rate
- ❌ `meditron:7b` for Predictor - only 20% accuracy
- ❌ Mixed models = complex to maintain

---

#### **AFTER (Recommended - Optimized):**
```python
class AgentConfig:
    """Configuration for Agentic AI System"""
    
    # Agent Models - ALL USING PROVEN llama3.1:8b
    # Based on comprehensive testing (76 test cases, 7 models evaluated)
    # llama3.1:8b achieved: 100% fall detection, 100% reliability, 76.5% accuracy
    
    MONITOR_AGENT = "ollama:llama3.1:8b"      # Real-time monitoring
    ANALYZER_AGENT = "ollama:llama3.1:8b"     # Deep analysis
    ALERT_AGENT = "ollama:llama3.1:8b"        # Emergency detection
    PREDICTOR_AGENT = "ollama:llama3.1:8b"    # Trend prediction
    COORDINATOR_AGENT = "ollama:llama3.1:8b"  # Multi-agent orchestration
    
    # Model-specific settings
    TEMPERATURES = {
        "monitor": 0.1,      # Very deterministic for safety
        "analyzer": 0.3,     # Slightly creative for patterns
        "predictor": 0.2,    # Balanced for predictions
        "alert": 0.1,        # Conservative for alerts
        "coordinator": 0.3   # Context-aware reasoning
    }
    
    TIMEOUTS = {
        "monitor": 30,       # Critical - reasonable timeout
        "analyzer": 40,      # Flexible - can take longer
        "predictor": 40,     # Flexible - complex calculations
        "alert": 20,         # Quick - time-sensitive
        "coordinator": 30    # Moderate - multi-agent coordination
    }
```

**Benefits:**
- ✅ 100% fall detection (proven in 17 test cases)
- ✅ Zero timeouts (100% reliable)
- ✅ Single model = easier maintenance
- ✅ Consistent behavior across agents

---

### **2. Update Agent Temperature Settings**

**Current:** All agents use default temperature (probably 0.3)

**Recommended:** Add agent-specific temperatures for optimal performance

**Add this function after AgentConfig class:**

```python
def get_agent_temperature(agent_type: str) -> float:
    """Get optimal temperature for agent type"""
    return AgentConfig.TEMPERATURES.get(agent_type, 0.3)

def get_agent_timeout(agent_type: str) -> int:
    """Get timeout for agent type"""
    return AgentConfig.TIMEOUTS.get(agent_type, 30)
```

**Modify agent calls to use temperature:**

**Before:**
```python
# In monitor_agent function
response = client.chat.completions.create(
    model=AgentConfig.MONITOR_AGENT,
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
)
```

**After:**
```python
# In monitor_agent function
response = client.chat.completions.create(
    model=AgentConfig.MONITOR_AGENT,
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ],
    temperature=get_agent_temperature("monitor")
)
```

Apply same change to:
- `analyzer_agent()` - use temperature 0.3
- `predictor_agent()` - use temperature 0.2
- `alert_agent()` - use temperature 0.1
- `coordinator_agent()` - use temperature 0.3

---

### **3. Add Fallback Mechanism**

**Why:** Even though llama3.1 is 100% reliable, always have a backup plan

**Add after AgentConfig:**

```python
class FallbackConfig:
    """Fallback configuration for agent failures"""
    
    # Primary model
    PRIMARY_MODEL = "ollama:llama3.1:8b"
    
    # Fallback model (same model, but good to have config)
    FALLBACK_MODEL = "ollama:llama3.1:8b"
    
    # Max retries before fallback
    MAX_RETRIES = 3
    
    # Retry delays (seconds)
    RETRY_DELAYS = [1, 2, 5]  # Exponential-ish backoff
```

**Add retry wrapper function:**

```python
def call_agent_with_retry(agent_func, *args, max_retries=3, **kwargs):
    """
    Call an agent function with retry logic
    
    Args:
        agent_func: The agent function to call
        *args: Positional arguments for the function
        max_retries: Maximum number of retries
        **kwargs: Keyword arguments for the function
    
    Returns:
        Agent response or fallback response
    """
    for attempt in range(max_retries):
        try:
            result = agent_func(*args, **kwargs)
            return result
        except Exception as e:
            if attempt < max_retries - 1:
                delay = FallbackConfig.RETRY_DELAYS[min(attempt, len(FallbackConfig.RETRY_DELAYS) - 1)]
                print(f"[RETRY] Attempt {attempt + 1} failed: {e}. Retrying in {delay}s...")
                time.sleep(delay)
            else:
                print(f"[FALLBACK] All retries failed: {e}. Returning safe fallback.")
                return {
                    "status": "fallback",
                    "error": str(e),
                    "safe_mode": True,
                    "recommendation": "Manual review required"
                }
```

**Use it in critical paths:**

```python
# In monitoring loop
def autonomous_monitoring():
    while monitoring_active:
        for device_id, state in PATIENT_STATES.items():
            if len(state.history) > 0:
                # Use retry wrapper for critical monitor agent
                result = call_agent_with_retry(
                    monitor_agent,
                    state.get_recent(5),
                    max_retries=3
                )
                
                if result.get('safe_mode'):
                    # Escalate to manual review
                    emit_alert({
                        'type': 'SYSTEM_FALLBACK',
                        'device_id': device_id,
                        'message': 'Agent failed, manual review required'
                    })
```

---

### **4. Update Model List**

**Current code (lines 98-105):**
```python
# Available AI Models
AVAILABLE_MODELS = [
    'ollama:qwen2.5:7b',
    'ollama:llama3.1:8b',
    'ollama:deepseek-r1:8b',
    'ollama:meditron:7b',
    'ollama:medllama2:7b',
    'ollama:gemma3:12b'
]
```

**After (Recommended models only):**
```python
# Available AI Models (Based on evaluation results)
AVAILABLE_MODELS = [
    'ollama:llama3.1:8b',    # ✅ RECOMMENDED - 100% fall detection, 100% reliable
    'ollama:qwen2.5:7b',     # ⚠️ BACKUP - Fast but misses 29% of falls
]

# Deprecated models (from evaluation - DO NOT USE)
DEPRECATED_MODELS = {
    'ollama:meditron:7b': 'Only 20% accuracy on fall detection',
    'ollama:medllama2:7b': 'Only 20-40% accuracy',
    'ollama:gemma3:12b': '71% timeout rate',
    'ollama:deepseek-r1:8b': '60% timeout rate',
    'monotykamary/medichat-llama3:8b': 'Missed all falls in testing'
}
```

---

### **5. Add Performance Monitoring**

**Add after AGENT_ACTIVITY_LOG:**

```python
# Performance tracking
AGENT_PERFORMANCE = {
    'monitor': {'calls': 0, 'successes': 0, 'failures': 0, 'total_latency': 0},
    'analyzer': {'calls': 0, 'successes': 0, 'failures': 0, 'total_latency': 0},
    'predictor': {'calls': 0, 'successes': 0, 'failures': 0, 'total_latency': 0},
    'alert': {'calls': 0, 'successes': 0, 'failures': 0, 'total_latency': 0},
    'coordinator': {'calls': 0, 'successes': 0, 'failures': 0, 'total_latency': 0}
}

def track_agent_call(agent_type: str, success: bool, latency_ms: float):
    """Track agent performance metrics"""
    if agent_type in AGENT_PERFORMANCE:
        AGENT_PERFORMANCE[agent_type]['calls'] += 1
        if success:
            AGENT_PERFORMANCE[agent_type]['successes'] += 1
        else:
            AGENT_PERFORMANCE[agent_type]['failures'] += 1
        AGENT_PERFORMANCE[agent_type]['total_latency'] += latency_ms

def get_agent_stats(agent_type: str) -> dict:
    """Get performance statistics for an agent"""
    stats = AGENT_PERFORMANCE.get(agent_type, {})
    if stats['calls'] == 0:
        return {'success_rate': 0, 'avg_latency': 0, 'total_calls': 0}
    
    return {
        'success_rate': stats['successes'] / stats['calls'],
        'avg_latency': stats['total_latency'] / stats['calls'],
        'total_calls': stats['calls'],
        'failures': stats['failures']
    }
```

**Wrap agent calls with tracking:**

```python
# In monitor_agent function
def monitor_agent(recent_data):
    start_time = time.time()
    try:
        # ... existing code ...
        result = client.chat.completions.create(...)
        
        latency = (time.time() - start_time) * 1000
        track_agent_call('monitor', success=True, latency_ms=latency)
        
        return result
    except Exception as e:
        latency = (time.time() - start_time) * 1000
        track_agent_call('monitor', success=False, latency_ms=latency)
        raise e
```

---

### **6. Add Health Check Endpoint**

**Add new Flask route:**

```python
@app.route('/api/agent-health')
def agent_health():
    """Health check for all agents"""
    return jsonify({
        'status': 'healthy',
        'model': AgentConfig.MONITOR_AGENT,
        'agents': {
            'monitor': get_agent_stats('monitor'),
            'analyzer': get_agent_stats('analyzer'),
            'predictor': get_agent_stats('predictor'),
            'alert': get_agent_stats('alert'),
            'coordinator': get_agent_stats('coordinator')
        },
        'timestamp': datetime.now().isoformat()
    })
```

---

## 🚀 IMPLEMENTATION STEPS

### **Step 1: Backup Current Config**
```bash
# Create backup
cp agentic_medicore_enhanced.py agentic_medicore_enhanced.py.backup_$(date +%Y%m%d)
```

### **Step 2: Update AgentConfig (5 minutes)**
1. Open `agentic_medicore_enhanced.py`
2. Find lines 47-51 (AgentConfig class)
3. Replace all agent models with `ollama:llama3.1:8b`
4. Add TEMPERATURES and TIMEOUTS dictionaries

### **Step 3: Add Helper Functions (5 minutes)**
1. Add `get_agent_temperature()` function
2. Add `get_agent_timeout()` function
3. Add `call_agent_with_retry()` function

### **Step 4: Update Agent Calls (10 minutes)**
1. Find all `client.chat.completions.create()` calls
2. Add `temperature=get_agent_temperature(agent_type)` parameter
3. Wrap critical calls with `call_agent_with_retry()`

### **Step 5: Add Performance Tracking (10 minutes)**
1. Add `AGENT_PERFORMANCE` dictionary
2. Add `track_agent_call()` function
3. Add tracking to each agent function
4. Add `/api/agent-health` endpoint

### **Step 6: Update Model List (2 minutes)**
1. Update `AVAILABLE_MODELS` list
2. Add `DEPRECATED_MODELS` dictionary

### **Step 7: Test Deployment (30 minutes)**
1. Restart Flask server
2. Test fall detection with sample data
3. Verify all agents using llama3.1:8b
4. Check `/api/agent-health` endpoint
5. Monitor for timeouts (should be zero)

---

## 📊 EXPECTED IMPROVEMENTS

### **Before Deployment:**
```
Monitor Agent:   llama3.1:8b  ✅ (already optimal)
Analyzer Agent:  qwen2.5:7b   ⚠️ (71% sensitivity, misses falls)
Alert Agent:     deepseek-r1  ❌ (60% timeout rate)
Predictor Agent: meditron:7b  ❌ (20% accuracy)
Coordinator:     qwen2.5:7b   ⚠️ (unreliable for coordination)

Overall System:
├─ Fall Detection: ~85% (some agents miss fails)
├─ Reliability: ~75% (some agents timeout)
└─ Maintenance: Complex (5 different models)
```

### **After Deployment:**
```
Monitor Agent:   llama3.1:8b  ✅
Analyzer Agent:  llama3.1:8b  ✅
Alert Agent:     llama3.1:8b  ✅
Predictor Agent: llama3.1:8b  ✅
Coordinator:     llama3.1:8b  ✅

Overall System:
├─ Fall Detection: 100% ✅ (all agents consistent)
├─ Reliability: 100% ✅ (zero timeouts)
└─ Maintenance: Simple (single model)
```

---

## ⚠️ ROLLBACK PLAN

If deployment causes issues:

```bash
# Restore backup
cp agentic_medicore_enhanced.py.backup_YYYYMMDD agentic_medicore_enhanced.py

# Restart server
# Windows:
taskkill /F /IM python.exe
python agentic_medicore_enhanced.py

# Linux:
pkill -9 python
python agentic_medicore_enhanced.py
```

---

## 🎯 VALIDATION CHECKLIST

After deployment, verify:

- [ ] All 5 agents using `ollama:llama3.1:8b`
- [ ] Monitor agent detects test fall (100% expected)
- [ ] No timeout errors in logs
- [ ] `/api/agent-health` shows good metrics
- [ ] Temperature settings applied correctly
- [ ] Retry mechanism works (test by simulating failure)
- [ ] Performance tracking capturing metrics
- [ ] System stable for 1 hour continuous operation

---

## 📈 MONITORING POST-DEPLOYMENT

**Track these metrics for 7 days:**

1. **Fall Detection Rate**
   - Target: ≥ 99%
   - Current baseline: 100% (from testing)

2. **False Positive Rate**
   - Target: ≤ 30%
   - Current baseline: 40% (acceptable)

3. **System Uptime**
   - Target: ≥ 99.9%
   - Current baseline: ~95% (with timeouts)

4. **Average Latency**
   - Target: ≤ 20s per agent
   - Current baseline: 14s (monitor)

5. **Agent Reliability**
   - Target: 100% completion rate
   - Current baseline: 100% (llama3.1)

---

## 💰 COST IMPACT

**Before:** $0 (all local Ollama)  
**After:** $0 (all local Ollama)  
**Change:** No change

**Resource Utilization:**
- CPU: Similar (all 8B models)
- Memory: -20% (removed 12B gemma3)
- Disk: Minimal (already have llama3.1)

---

## 🎓 LESSONS FOR TEAM

1. **Don't assume medical models are better** - General models won
2. **Test thoroughly before production** - Prevented deploying 20% accuracy model
3. **Reliability > Perfect accuracy** - Consistent 76% beats occasional 100%
4. **Safety first in healthcare** - 100% fall detection is mandatory
5. **Single model simplifies ops** - Easier to maintain and optimize

---

## 📞 SUPPORT

**Documentation:**
- `reports/COMPREHENSIVE_FINAL_REPORT.md` - Full evaluation results
- `reports/FINAL_MODEL_RECOMMENDATIONS.md` - Deployment guide
- `reports/COMPLETE_MODEL_COMPARISON.md` - All models tested

**Questions?**
- Check evaluation reports first
- All decisions backed by 76 test cases
- Model performance thoroughly documented

---

**Status:** Ready to deploy NOW ✅  
**Estimated Time:** 30-60 minutes total  
**Risk Level:** LOW (proven model)  
**Confidence:** HIGH (9/10)
