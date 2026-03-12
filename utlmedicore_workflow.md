# UTLMediCore — System Workflow Diagrams

## 1. End-to-End Data & Agent Pipeline

```mermaid
flowchart TD
    A["IoT Sensor - IMU / HR / SpO2 Wristband"] -->|HTTP POST| B["Flask + SocketIO - port 7000"]

    B --> C["PatientState - RAM deque max 100 pts"]
    B --> D[("MongoDB - Raw time-series")]

    C --> E{"Smart Memory Trigger?"}
    E -->|"Fall / Abnormal HR / Hypoxia"| F["store_sensor_snapshot - CRITICAL"]
    E -->|"Every 50 routine readings"| G["store_sensor_snapshot - Routine"]

    F --> H["run_async - asyncio.Lock - bg thread"]
    G --> H

    H --> I["Graphiti.add_episode()"]

    I --> J["llama3.1:8b - Entity extraction"]
    I --> K["nomic-embed-text - 768-dim embedding"]
    J --> L[("Neo4j Knowledge Graph")]
    K --> L

    C -->|"Every 10s"| M["CoordinatorAgent - coordinate_analysis()"]

    M --> N["MonitorAgent - Anomaly Detection"]
    M --> O["AlertAgent - create_alert()"]
    M --> P["AnalyzerAgent - Pattern and Trend"]
    M --> Q["PredictorAgent - Risk Forecast"]

    N -->|"Anomaly found"| R["Two-Tier Memory Query"]
    R --> N
    O --> L

    P --> S[("Opik - LLM Observability")]
    Q --> S

    M -->|"emit events"| T["Web Dashboard - SocketIO push"]
    M --> U["AGENT_ACTIVITY_LOG - last 100"]
```

---

## 2. Two-Tier Memory Retrieval Strategy

```mermaid
flowchart TD
    IN["Incoming Query"] --> T1A

    subgraph TIER1["TIER-1 — Graphiti Semantic Search"]
        T1A["graphiti.search(query, group_ids)"]
        T1B["nomic-embed-text vectorizes query"]
        T1C["Cosine search over EntityEdge vectors"]
        T1D["Structured FACTS returned"]
        T1A --> T1B --> T1C --> T1D
    end

    T1D -->|"Result OK"| OK1["Use Tier-1 Facts - memory_status: active"]
    T1D -->|"Empty or Timeout"| T2A

    subgraph TIER2["TIER-2 — Direct Neo4j Read (no Lock)"]
        T2A["run_async_readonly() - never blocked"]
        T2B["Cypher: MATCH Episodic WHERE group_id = patient - LIMIT 10"]
        T2C["Raw episode text - No Ollama call needed"]
        T2A --> T2B --> T2C
    end

    T2C -->|"Result OK"| OK2["Use Tier-2 Episodes - memory_status: active"]
    T2C -->|"Also empty"| NONE["No history yet - memory_status: empty"]
```

---

## 3. AI Chatbot Request Lifecycle — /api/memory-chat

```mermaid
sequenceDiagram
    actor Nurse
    participant UI as "Agentic Interface"
    participant API as "Flask /api/memory-chat"
    participant MEM as "PatientMemory 2-Tier"
    participant RAM as "PatientState RAM"
    participant LLM as "lfm2.5-thinking:1.2b"
    participant OPK as "Opik Tracing"

    Nurse->>UI: Types question
    UI->>API: POST question + device_id + history last 8 turns

    API->>MEM: get_patient_context(question)
    MEM-->>API: Tier-1 facts OR Tier-2 raw episodes

    API->>RAM: get_recent(n=3) + ACTIVE_ALERTS last 3
    RAM-->>API: Live vitals + recent alerts

    API->>API: Build system_prompt with memory + vitals + alerts
    API->>LLM: chat.completions.create temperature 0.3
    LLM-->>OPK: track name=memory_chatbot
    LLM-->>API: Raw answer - strip think tags

    API-->>UI: answer + memory_status + memory_preview
    UI-->>Nurse: Display response in chat bubble
```

---

## 4. AI Insight Cards — /api/memory-insights

```mermaid
flowchart TD
    REQ["GET /api/memory-insights?device_id=DCA"] --> Q1
    REQ --> Q2
    REQ --> Q3
    REQ --> Q4

    Q1["Query: risk_profile"]
    Q2["Query: vitals_pattern"]
    Q3["Query: location_habits"]
    Q4["Query: recommendations"]

    Q1 --> MEM["Two-Tier Retrieval per query"]
    Q2 --> MEM
    Q3 --> MEM
    Q4 --> MEM

    MEM --> HIT{"memory_hits count"}
    HIT -->|"1 or more"| SA["memory_status: active"]
    HIT -->|"0"| SE["memory_status: empty"]

    SA --> PROMPT["Build LLM Prompt - 4 context blocks trimmed to 800 chars each"]
    SE --> PROMPT

    PROMPT --> LLM["lfm2.5-thinking:1.2b - tracked by Opik"]

    LLM --> PARSE["Robust JSON Parser"]
    PARSE --> PA["strip think tags"]
    PARSE --> PB["strip markdown fences"]
    PARSE --> PC["normalize field names"]
    PARSE --> PD["validate severity enum"]

    PA --> OUT{"Parse OK?"}
    PB --> OUT
    PC --> OUT
    PD --> OUT

    OUT -->|"Yes"| CARDS["4 Insight Cards - title + summary + severity"]
    OUT -->|"No"| FALL["Fallback: 4 hardcoded live-vitals cards"]

    CARDS --> RESP["Response JSON - insights + memory_status + memory_hits + live_vitals"]
    FALL --> RESP
```

---

## 5. Technology Stack Overview

```mermaid
graph TB
    subgraph FRONTEND["Frontend - Browser"]
        UI["agentic_interface_enhanced.html\nHTML + CSS + JS + SocketIO client"]
    end

    subgraph BACKEND["Backend - Flask port 7000"]
        FLASK["agentic_medicore_enhanced.py"]
        AGENTS["5 Agents: Monitor, Alert, Analyzer, Predictor, Coordinator"]
        MEM_MOD["memory/patient_memory.py\nrun_async + run_async_readonly"]
        GRAPH_C["memory/graphiti_client.py\nGraphiti singleton"]
        FLASK --> AGENTS
        AGENTS --> MEM_MOD
        MEM_MOD --> GRAPH_C
    end

    subgraph AI["AI Layer - Local Ollama port 11434"]
        LFM["lfm2.5-thinking:1.2b\nAll agents + Chatbot + Insights"]
        LLAMA["llama3.1:8b\nEntity extraction only"]
        NOMIC["nomic-embed-text\n768-dim semantic embeddings"]
    end

    subgraph STORAGE["Storage"]
        NEO[("Neo4j - Knowledge Graph\nEpisodicNode, EntityNode, EntityEdge")]
        MONGO[("MongoDB\nRaw time-series per device")]
    end

    subgraph OBS["Observability"]
        OPIK["Opik - LLM call tracing"]
        ACTLOG["AGENT_ACTIVITY_LOG\nLast 100 activities"]
    end

    UI <-->|"WebSocket SocketIO"| FLASK
    FLASK --> MONGO
    GRAPH_C --> LFM
    GRAPH_C --> LLAMA
    GRAPH_C --> NOMIC
    GRAPH_C <--> NEO
    AGENTS -->|"@track decorator"| OPIK
    AGENTS --> ACTLOG
```

---

*UTLMediCore — Multi-Agent Patient Monitoring System*
*Architecture as of March 2026*
