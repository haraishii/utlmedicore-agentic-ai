# 🧠 Detailed Guide: CrewAI Workflow in UTLMediCore
## Module: `insights/report_crew.py`

> **Document Status**: Technical Explanation & Architecture  
> **Date**: March 16, 2026  

---

## 📋 1. Core Concept: Why Use an AI Crew?

Asking a **single AI model** to analyze medical numbers *and* write a professional report simultaneously can overwhelm it. This often leads to "hallucinations" (mixed numbers) or reports that are too technical for nurses to quickly read.

**CrewAI** solves this using **Multi-Agent Collaboration**. The system runs two AI "agents" with distinct expertise sequentially (*Sequential Process*), mimicking a real-world medical consultation meeting.

---

## 🛠️ 2. The Team Structure (The Crew)

Inside `insights/report_crew.py`, we define **Two Intelligent Agents**:

### 📊 Agent 1: Healthcare Data Analyst (The Numbers Expert)
**Task**: Ingests raw numbers and looks for anomalies or trend regressions.  
**Character**: Highly mathematical, focuses on high/low peaks, and cares less about flowery language.  

```python
# report_crew.py [Lines 42-49]
data_analyst = Agent(
    role='Healthcare Data Analyst',
    goal='Analyze patient vital signs and activity patterns',
    backstory='''Expert in analyzing patient monitoring data 
    with 15 years of experience in healthcare analytics.''',
    llm=self.llm,
    verbose=False
)
```

---

### ✍️ Agent 2: Clinical Report Writer (The Medical Author)
**Task**: Ingests Agent 1's analysis and translates it into a professional summary.  
**Character**: Compassionate, polite, and structure-driven (utilizes strictly Markdown headers).  

```python
# report_crew.py [Lines 51-58]
clinical_writer = Agent(
    role='Clinical Report Writer',
    goal='Create clear, actionable patient health summaries',
    backstory='''Medical writer specializing in patient reports 
    for healthcare professionals. Known for clarity and actionable insights.''',
    llm=self.llm,
    verbose=False
)
```

---

## ⚙️ 3. Execution Pipeline (Step-by-Step)

### **Step 1: Raw Data Aggregation**
The Python backend aggregates MongoDB live readings and Neo4j graphitti historical nodes into a single structured string (`data_summary`):

```python
# report_crew.py [Lines 60-85]
data_summary = f"""
PATIENT: {patient_id}
RISK SCORE: {risk_score} 
VITAL SIGNS: {json.dumps(vital_signs, indent=2)}
ACTIVITIES: {json.dumps(activities, indent=2)}
LOCATIONS: {json.dumps(locations, indent=2)}
NUTRITION: {json.dumps(nutrition, indent=2)}
MEMORY INSIGHTS: {graphiti_summary}
"""
```

---

### **Step 2: Task 1 — Structured Health Analysis**
Agent 1 is tasked with strictly searching for health trends, critical alerts, and safe parameters over the past specified hours:

```python
# report_crew.py [Lines 87-103]
analysis_task = Task(
    description=f'''
    Analyze this patient's health data and identify:
    1. Overall health status
    2. Key patterns or trends
    3. Areas of concern
    4. Positive findings
    ''',
    agent=data_analyst,
    expected_output='Structured health analysis with key findings'
)
```

---

### **Step 3: Sequential Baton-Passing**
Once analysis finishes, the Analyst passes the structured finding string to Agent 2. The Writer does not see raw points anymore; they act on the parsed conclusions to compile:

```python
# report_crew.py [Lines 105-122]
narrative_task = Task(
    description='''
    Based on the analysis, write a professional patient health summary.
    Format as markdown with sections:
    1. **Executive Summary**
    2. **Health Status Overview**
    3. **Key Findings**
    4. **Recommendations**
    ''',
    agent=clinical_writer,
    expected_output='Professional markdown patient report'
)
```

---

### **Step 4: Crew Execution (Orchestration)**
The system groups tasks and agents together into a **Crew** running sequentially:

```python
# report_crew.py [Lines 125-130]
crew = Crew(
    agents=[data_analyst, clinical_writer],
    tasks=[analysis_task, narrative_task],
    process=Process.sequential, # <-- Forces Agent 1 to finish BEFORE Agent 2 begins
    verbose=False
)
```

---

## 🛡️ 4. Resilience Framework (Fallback)

To ensure the system **NEVER FAILS** to write medical documentation (even if cloud models time-out or network splits), the kickoff is wrapped in extreme error handling:

```python
# report_crew.py [Lines 132-139]
try:
    result = crew.kickoff()  # <-- Triggers the consultation
    return str(result)
except Exception as e:
    # IF ERROR (timeout / internet split), BACKUP TEMPLATE FIRES:
    return self._fallback_narrative(patient_id, risk_score, alerts, graphiti_summary)
```

---

## 📊 1. Overview: Continuous Monitoring Data Reading Flow

To understand the core reporting agent, we must look at how data moves from the patient’s body into the "Agentic Mind."

### **The Ingestion Pipeline**
1.  **IoT Stream to MongoDB**: 
    The wearable device pushes sub-second packets (e.g., `Heart_Rate`, `Blood_oxygen`, `Step`, `Calories`) into **MongoDB**.
2.  **State Aggregation**: 
    The Python backend listens to that collection. It maintains a memory class that sums durations (e.g., "Total resting hours") or flags thresholds (e.g., "Critical SpO2 alert").
3.  **Graphitti Injection**: 
    If a data packet is notable or hits a snapshot timer, the agent triggers an **Episodic Narrative** and embeds it into the **Neo4j Graph Database**. This creates a relationship graph (e.g., *Patient* `[:LOCATES]` *Living Room*).
4.  **Prompt Concatenation**: 
    When report-generating begins, the backend converts raw JSON into a readable **Structured Data Summary Envelope**. CrewAI agents do not query the SQL or Mongo databases directly; they consume this aggregated prompt containing both immediate values and long-term trend nodes.

---

## ⚖️ 2. Architectural Comparison: CrewAI Framework vs. Lite Agent Prompting

The UTLMediCore system utilizes two distinct agentic styles to solve reporting. Understanding their difference adds immense depth to the architecture:

### **A. CrewAI Framework (`report_crew.py`)**
*This uses structured autonomous Agents utilizing `Crew()`, `Agent()`, and `Task()` classes.*

-   **Mechanism**: Modelled after a human staff consult. An Agent is given a **Goal** and a **Backstory** (e.g., "Expert Analyst with 15 years experience"). 
-   **Interaction style**: CrewAI manages the pipeline iteratively using `Process.sequential`. It wraps failures natively and ensures Agent 2 explicitly builds on top of the `.expected_output` of Agent 1.
-   **Pros**: Highly modular, handles "thinking" intervals cleanly on larger parameter backends (cloud models), and shields standard code from formatting issues because tasks enforce response styling naturally.

### **B. Lite Analyst Agent (`lite_report_agent.py`)**
*This uses raw sequential LLM prompting back-to-back inside standard Python loops.*

-   **Mechanism**: **Phase 1 Prompt** asks a model to execute "Correlation Analyst" logic. It receives the raw string back. Then it appends that output into a **Phase 2 Prompt** forcing a "Clinical Officer" style to re-run and format it.
-   **Pros**: Extreme speed and execution logic control. 100% predictable back-to-back execution without background framework dependencies.
-   **Cons**: No native "fallback/debate" capabilities if formatting breaks midway. Requires heavier regex parsing if variables crash.

| Attribute | CrewAI Orchestration | Lite Agent Prompting |
| :--- | :--- | :--- |
| **Backstory Persona** | ✅ Fully supported via `.backstory` | ❌ Simluated purely inside instructions |
| **Resilience** | ✅ Structured error handlers per task | ⚠️ Manual `try-except` wrappers |
| **Framework Size** | Medium (Requires `crewai` pip) | Zero (Pure string manipulation) |
| **Usage Intent** | Best for high-complexity deep reasoning | Best for fast, deterministic sub-queries |

---

## 📈 3. Actionable Visual: Full Narrative Render

When the **Crew executes kickoff()**, the resulting response is not merely a string of numbers. It outputs a full formatted Markdown dashboard comprising:
-   **Pulse-Line Diagnostics**: Highlighting correlation statements like: *"We noted Heart Rate spiking specifically during Bathroom visits."*
-   **Corrective Warnings**: Highlighting: *"Step deficits logged for 3 consecutive hours."*

This multi-faceted intelligence provides caretakers with **Explanatory Diagnosis (Why)** instead of raw metrics reporting (What).
