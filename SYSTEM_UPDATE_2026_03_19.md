# 🏥 UTLMediCore System Update
**Date:** March 19, 2026 — 06:06 WIB (Taipei, UTC+8)  
**Version:** `v1.2.0-cloud-integration`

> **Summary:** Successfully integrated Ollama Cloud LLM for Graphiti memory graph extraction, replacing the slower local LLaMA 8B model. Included the implementation of a custom time-range report generation UI.

---

## ☁️ 1. Graphiti Cloud LLM Integration

### 🔴 The Challenge
The local LLaMA 8B model used for Graphiti entity extraction was experiencing significant latency and had a constrained context window. This resulted in delayed updates (30–60 minutes late) to the Neo4j graph, rendering memory-based context unreliable for real-time clinical AI decisions.

### 🟢 The Solution (`memory/graphiti_client.py`)
**Architecture Upgrade — `OllamaCloudLLMClient` class:**
- Developed a proper subclass of Graphiti's `LLMClient` ABC, fully implementing the `_generate_response()` abstract method.
- Integrated the **native `ollama.Client`** Python library for reliable protocol communication.
- Enabled token-based authentication via `Authorization: Bearer <key>`.
- Implemented asynchronous execution using `asyncio.to_thread()` to prevent event loop blocking.
- Inherits core features naturally: `set_tracer()`, retry logic, and caching.

**Dynamic Configuration:**
```python
# Target Cloud Extraction Model:
GRAPHITI_CLOUD_MODEL = os.getenv("GRAPHITI_CLOUD_MODEL", "mistral-large-3:675b")

# Local Fallback Model:
GRAPHITI_LOCAL_MODEL = os.getenv("GRAPHITI_LLM_MODEL", "llama3.1:8b")
```

**Model Performance Matrix:**
| Model | Latency | Status / Remarks |
|:---|:---|:---|
| `mistral-large-3:675b` | Medium | ✅ Active — Optimal accuracy |
| `kimi-k2-thinking` | Slower | ✅ Reliable — Extended 200k context |
| `glm4.7:cloud` | Faster | ⚠️ Pending authorization |

### 🐛 Debugging Journey
| Error Encountered | Root Cause | Resolution |
|:---|:---|:---|
| `NameError: _graphiti_instance` | Variable accidentally removed | Restored variable definition |
| `Connection error` | URL typo (`ollama.ai` vs `ollama.com`) | Corrected endpoint URL |
| `JSONDecodeError` | Protocol mismatch w/ OpenAI endpoint | Switched to native `ollama.Client` |
| `AttributeError: set_tracer` | Missing ABC inheritance | Added proper `LLMClient` inheritance |

---

## 📊 2. Custom Time Range Reports

### 🔴 The Challenge
Report generation was constrained to fixed periods (daily, weekly, monthly). Users requested the ability to generate specific short-term targeted reports (e.g., last 3 hours).

### 🟢 The Solution
**Backend Integration (`agentic_medicore_enhanced.py`):**
- Extended the `/api/report/generate` endpoint to accept `period: "custom"` with a dynamic `hours` parameter (1–168 hours).
- Reports are now automatically routed to a new `reports/custom/` directory.

**Frontend Integration (`agentic_interface_enhanced.html`):**
- Introduced a **Custom Time Range** section with quick-action buttons: `1h`, `3h`, `6h`, `12h`.
- Added a reliable fallback mechanism for patient ID fetching from the DOM.
- Upgraded the `generateReport()` JS function to support custom hour payloads.

---

## 🏗️ 3. Hybrid Graph Write Architecture

### 💡 The Strategy
To prevent the "frozen graph" effect caused by LLM processing delays (30–90 seconds per episode), we introduced a **Two-Layer Write Architecture**:

1. **Direct Neo4j Write (Layer 1):** Instant (<1s) writes for structured sensor data (HR, SpO2, Posture). Bypasses LLM entirely.
2. **Graphiti + LLM (Layer 2):** Intelligent entity extraction for critical events or throttled routine observations (1x per hour).

**Implementation Details:**
- Created `memory/direct_neo4j_writer.py` for synchronous, low-latency Neo4j transactions.
- Added strict 90-second episode timeouts to prevent async queue blocking.

*Log maintained by UTLMediCore AI System — Antigravity Agent*
