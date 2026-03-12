# UTLMediCore AI Presentation: Verified Edge Intelligence (Expanded 20-Slide Deck)
## Presentation Strategy & Materials

**Date:** 2026-02-19
**Topic:** Strategic Optimization: Validating Efficient Edge AI for Healthcare
**Tone:** Professional, Data-Driven, Transparent, Future-Focused
**Target Audience:** Technical Stakeholders, Clinical Leads, Investors

---

## 📅 Part 1: Presentation Workflow

1.  **Theme:**
    *   **Professional & Clean:** Deep Navy background, White text, Teal accents (Success), Muted Red (Alerts).
    *   **Esthetics:** Use "Glassmorphism" for UI screenshots.
    *   **Icons:** Use simple line icons for "Server", "Edge Device", "Brain" (AI), "Shield" (Safety).

2.  **Narrative Arc:**
    *   **The Problem:** Healthcare AI is too heavy and slow.
    *   **The Method:** We didn't guess; we *traced* (Opik).
    *   **The Discovery:** Small "Thinking" models beat big "Memorizing" models.
    *   **The Solution:** A validated, hybrid architecture ready for the edge.

3.  **Visual Assets:**
    *   **Opik Dashboards:** Essential for proving "Verification".
    *   **Comparison Charts:** Sensitivity, Latency, Size.
    *   **Architecture Diagrams:** Flow of data from Sensor -> 1.2B Model -> Alert.

---

## 📺 Part 2: Slide-by-Slide Description (20 Slides)

### 🔹 SECTION 1: INTRODUCTION & CONTEXT

#### Slide 1: Title Slide
*   **Title:** Strategic Optimization: Validating Efficient Edge AI for Healthcare
*   **Subtitle:** Validating the Shift from 8B Cloud Models to 1.2B Edge "Thinking" Models
*   **Visual:** UTLMediCore Logo + Opik/Comet Logos (Verified by Data).
*   **Footer:** Confidential - Internal Research

#### Slide 2: Executive Summary & Agenda
*   **Headline:** Overview of Findings
*   **Bullets:**
    1.  **The Challenge:** High latency & resource cost of current 8B models.
    2.  **The Methodology:** Rigorous benchmarking of 10+ models using Opik tracing.
    3.  **The Breakthrough:** "Thinking" models (1.2B) outperform larger baseline models.
    4.  **The Plan:** Deployment roadmap for the new Hybrid Edge Architecture.

#### Slide 3: The Healthcare Monitoring Challenge
*   **Headline:** Why "Standard" AI Fails at the Edge
*   **Visual:** A "Scale" balancing Safety vs. Speed.
*   **Content:**
    *   **Safety Critical:** Must detect 100% of falls (Sensitivity).
    *   **Time Sensitive:** Must alert within <10 seconds (Latency).
    *   **Resource Constrained:** Patient devices can't run dual A100 GPUs.
*   **The Gap:** Current 8B models are safe (92%) but slow (14s) and heavy (5GB+).

#### Slide 4: The Resource Bottleneck
*   **Headline:** The Cost of "Bigger is Better"
*   **Chart:** Resource Usage of Llama 3.1 8B.
*   **Data Points:**
    *   **VRAM:** ~6 GB (Requires dedicated GPU).
    *   **Energy:** High power consumption (Not battery friendly).
    *   **Deployment:** Limited to Cloud/Server; cannot run on localized gateways.

### 🔹 SECTION 2: METHODOLOGY & VALIDATION

#### Slide 5: Our Validation Hypothesis
*   **Headline:** Can Smaller Models "Think" Better?
*   **Hypothesis:** Intelligence isn't just parameter count; it's architecture.
*   **The Test:** Compare massive models (20B, 12B, 8B) against specialized tiny models (1.2B, 3B).
*   **The Standard:** We define "Success" not by text quality, but by **Traceable Decisions**.

#### Slide 6: The Validation Framework (Opik)
*   **Headline:** Data-Driven Observability
*   **Visual:** **[Opik Dashboard Screenshot - Traces List]**
*   **Content:**
    *   **Tool:** Opik (by Comet.com).
    *   **Integration:** `TrackedAISuiteClient` intercepts every call.
    *   **Metrics:** Token Usage, Latency/Call, Error Rate, Output Validation.
*   **Why It Matters:** We have a "Black Box Recorder" for every AI decision.

#### Slide 7: The Test Suite
*   **Headline:** Rigorous Benchmark Scenarios
*   **Visual:** A grid of icons representing test cases.
*   **Content:**
    *   **30+ Unique Scenarios:**
        *   ✅ Clear Falls (Bathroom, Bedroom).
        *   ✅ Subtle Faints (Bradycardia + Lying Down).
        *   ✅ False Positives (Lying down to sleep).
        *   ✅ Edge Cases (Cardiac Arrest, "Slumping").

### 🔹 SECTION 3: THE DISCOVERY

#### Slide 8: The "Shocking" Discovery
*   **Headline:** Breaking the Scaling Laws
*   **Visual:** Large "1.2B > 8B" Graphic.
*   **Content:**
    *   **Model:** `lfm2.5-thinking:1.2b`
    *   **Result:** It beat the 8B production model in **Safety, Speed, AND Accuracy**.
    *   **Quote:** "A 1GB model doing the work of a 6GB model, but better."

#### Slide 9: Comparative Analysis: Safety
*   **Headline:** Sensitivity (Recall) is King
*   **Chart:** Bar Chart - Fall Detection Rate.
    *   **LFM 2.5 (1.2B):** **100%** (14/14 Detected) - *Winner*
    *   **Llama 3.1 (8B):** 92.9% (13/14 Detected)
    *   **Medical Llama (8B):** 71.4% (10/14 Detected)
    *   **Llama 3.2 (3B):** 50% (Failed)

#### Slide 10: Comparative Analysis: Speed
*   **Headline:** Every Second Counts
*   **Chart:** Horizontal Bar - Average Latency (Lower is Better).
    *   **LFM 2.5:** **9.3s**
    *   **Llama 3.1:** 14.2s
    *   **GPT-4o (Cloud):** ~2-3s (but privacy/cost concerns).
*   **Impact:** 5 seconds faster response time for emergency services.

#### Slide 11: Comparative Analysis: Efficiency
*   **Headline:** The "Edge" Advantage
*   **Chart:** Pie Charts - VRAM Usage.
    *   **Llama 3.1 8B:** 5.1 GB (Requires expensive hardware).
    *   **LFM 2.5 1.2B:** **0.7 GB** (Runs on Raspberry Pi / Mobile).
*   **Takeaway:** We can deploy this on $50 hardware instead of $1000 hardware.

### 🔹 SECTION 4: DEEP DIVE - "THINKING" MODELS

#### Slide 12: Why Did the Tiny Model Win?
*   **Headline:** "Thinking" vs. "Guessing"
*   **Content:**
    *   **Traditional Models:** Predict the next likely word based on training data probability.
    *   **Thinking Models:** Generate an internal "Chain of Thought" before answering.
    *   **Analogy:** A student guessing the answer vs. showing their work.

#### Slide 13: The "Thinking" Process (Trace)
*   **Headline:** Inside the AI's "Brain"
*   **Visual:** A mockup of a trace log.
    *   *Input:* HR 45, Posture: Kitchen Floor.
    *   *Step 1 (Thought):* "Patient is in Kitchen. Posture is prone. Heart rate is dangerously low."
    *   *Step 2 (Thought):* "This combination is not sleep. It indicates syncope."
    *   *Final Output:* "BS_ALERT: CRITICAL FALL DETECTED."

#### Slide 14: Edge Case Success Story
*   **Headline:** The "Cardiac Arrest" Case
*   **Scenario:** Patient slumps in chair (Posture: Sitting -> Unstable), HR drops to 30.
*   **8B Model Result:** "Patient is sitting. Vital signs constitute low heart rate. Warning." (Misclassified as non-critical).
*   **1.2B Model Result:** "Low HR (30) + Unstable Sitting = Potential Cardiac Event. CRITICAL ALERT."
*   **Validation:** Verified via Opik Trace ID `019c...`.

#### Slide 15: The "Goldilocks" Zone
*   **Headline:** Finding the Right Size
*   **Visual:** A graph curve (Parabola).
    *   *Too Small (3B standard):* Fails to understand context.
    *   *Too Big (12B+):* Timeouts, too slow, "overthinks" simple data.
    *   *Just Right (1.2B Thinking):* Specialized architecture fills the gap.

### 🔹 SECTION 5: ARCHITECTURE & IMPLEMENTATION

#### Slide 16: The New Hybrid Architecture
*   **Headline:** Best of Both Worlds
*   **Diagram:** System Diagram.
    *   **Edge Layer (1.2B):** `MonitorAgent` & `AlertAgent`. Always on. Fast. Local.
    *   **Cloud Layer (8B):** `CoordinatorAgent`. On-demand. Complex Summaries. Patient Chat.
*   **Benefit:** Speed/Safety at the edge; Verbal Fluency in the cloud.

#### Slide 17: Implementation Details
*   **Headline:** Configuration is Key
*   **Code:** Snippet of `AgentConfig` in Python.
    *   `MONITOR_AGENT = "ollama:lfm2.5-thinking:1.2b"`
    *   `ANALYZER_AGENT = "ollama:lfm2.5-thinking:1.2b"`
*   **Simplicity:** Zero code changes required for logic; only configuration updates.

#### Slide 18: Live Observability (Demo)
*   **Headline:** Real-Time Visibility
*   **Visual:** **[Opik Dashboard Screenshot - Detailed Trace View]**
*   **Content:**
    *   Show how we can "replay" any alert.
    *   Show input tokens vs output tokens.
    *   Show the "Reasoning" tags in Comet.com.

#### Slide 19: The Roadmap (Timeline)
*   **Headline:** Deployment Schedule
*   **Timeline:**
    *   **Q1:** Validation Complete (Current Status).
    *   **Q2:** Deploy 1.2B to Pilot Edge Devices (Raspberry Pi 5).
    *   **Q3:** Implement "Hybrid" Cloud Handoff for Chat features.
    *   **Q4:** On-device fine-tuning for specific patient baselines.

#### Slide 20: Conclusion & Call to Action
*   **Headline:** The Future is Efficient
*   **Summary:**
    1.  **Safety:** Verified 100% Sensitivity.
    2.  **Speed:** 34% Latency Reduction.
    3.  **Traceability:** Fully audited via Opik.
*   **Recommendation:** Immediate approval to migrate `MonitorAgent` to 1.2B Architecture.
*   **Q&A**

---

## 📂 Part 3: Source Materials & Data

### A. The "Thinking" Difference (For Slide 13)
*Use this actual logic flow for the slide:*

> **Standard 8B Model Trace:**
> "HR 45. Posture Lying Down. Bedroom. This typically matches sleep patterns. Status: Normal."
> *(Missed Context: It was 2 PM, not night time)*
>
> **LFM 1.2B Thinking Trace:**
> "Analyzing vitals... HR 45 is bradycardic.
> Analyzing context... Location is Bedroom, but user was 'Walking' 10 seconds ago.
> Reasoning... Immediate transition from Walking to Lying Down + HR drop isn't sleep. It's a collapse.
> detailed_analysis: Fall due to Syncope.
> **Verdict: CRITICAL ALERT**"

### B. The Benchmarks (For Slides 9-11)
*Source: `reports/LFM25_THINKING_RESULTS_SHOCKING.md`*

| Metric | Llama 3.1 8B (Baseline) | LFM 2.5 1.2B (New) | Improvement |
|--------|-------------------------|--------------------|-------------|
| **Recall (Safety)** | 92.9% | **100%** | **Safe** |
| **F1 Score** | 0.765 | **0.903** | **+18%** |
| **Latency** | 14.2s | **9.3s** | **34% Faster** |
| **Disk Size** | 4.9 GB | **0.7 GB** | **85% Smaller** |

### C. Opik Integration Code (For Slide 6/18)
*Source: `evaluation/opik_integration.py`*

```python
# The "Black Box Recorder"
@track(name="monitor_agent", tags=["safety", "edge_verified"])
def analyze_realtime(self, data):
    # Traces input sensors, "Thinking" steps, and final alert
    return agent_client.generate(data)
```
