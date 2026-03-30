<div align="center">

# UTLMediCore - Agentic AI
**Intelligent Health Monitoring & Clinical Reporting System**

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-Backend-green.svg)](https://flask.palletsprojects.com/)
[![Neo4j](https://img.shields.io/badge/Neo4j-Knowledge_Graph-blue.svg)](https://neo4j.com/)
[![CrewAI](https://img.shields.io/badge/CrewAI-Agentic_Reporting-orange.svg)](https://crewai.com/)
[![Docker](https://img.shields.io/badge/Docker-Supported-informational.svg)](https://www.docker.com/)

</div>

---

## About
**UTLMediCore Agentic AI** is a comprehensive health platform built around three core pillars:
1. **Intelligent Health Monitoring**: Continuous, real-time physiological tracking (Heart Rate, SpO2, Posture) paired with autonomous AI anomaly detection.
2. **Interactive Graph Memory Chat**: A responsive conversational interface powered by a **Neo4j Knowledge Graph**, allowing the AI to recall long-term patient histories, correlate complex health data, and provide deeply contextual medical insights.
3. **Manual Context Input**: Integrated logging forms that allow patients to capture precise daily events (meals, exercise, and sleep states) directly into the Neo4j graph, giving the AI a holistic understanding of the patient's lifestyle.

---

## Key Features
1. **Agentic Insight Generator**: Employs Multi-Phase Cognitive Reasoning to generate daily or custom-period (1-168 hours) medical reports.
   - Phase 1 (Analyst): Discovers correlations between activities/meals and vital sign fluctuations.
   - Phase 2 (Clinical Writer): Structures the insights using professional clinical terminology.
2. **Hybrid Graph-Memory Engine**: Maintains an interactive data structure via Neo4j and Graphiti AI.
   - Direct Database Write for ultra-low latency (< 1 second) storage of raw sensor metrics.
   - Entity Extraction System (LLM-driven) to comprehend manual log contexts and convert them into logical graph relationships.
3. **Cloud & Local LLM Ready**: Seamless integration via Ollama to toggle between cost-free local LLM processing (e.g., llama3.1:8b) and Cloud APIs (e.g., mistral-large-3:675b / kimi-k2-thinking) for intensive cognitive reasoning tasks.
4. **Manual Context Entry**: A responsive interface enabling users to log meals, activities, and medical history. All entries are rigorously calibrated to the local reference timezone (UTC+8).
5. **Bento Dashboard UI**: A modern interface for monitoring system diagnostics, checking MongoDB/Neo4j database connections, and downloading AI-generated HTML reports.

---

## System Architecture

1. **Frontend (Bento Dashboard)**
   Built with HTML/CSS/JS via Flask Templates. It features forms for manual context entry and interactive report generation triggers.
2. **Backend (Python / Flask)**
   The `agentic_medicore_enhanced.py` acts as the primary router, orchestrating data traffic between the frontend, the Neo4j memory system, and the CrewAI agentic layer.
3. **Database Layer**
   - MongoDB: Functions as the data lake for storing raw IoT appliance logs.
   - Neo4j: The core Knowledge Graph engine responsible for linking entities. For instance, `(Patient)-[:HAD_READING]->(HeartRate)` is cross-referenced with `(Patient)-[:CONSUMED]->(Spicy Meal)`.
4. **Agent Layer (CrewAI / Lite Agent)**
   When a report generation request is triggered, the Agent retrieves the entire memory graph from Neo4j. The LLM systematically evaluates the data, detects physiological anomalies, and drafts the clinical report.

---

## Core Directory Structure

```text
utlmedicore-agentic-ai/
├── agentic_medicore_enhanced.py  # Main Entry Point (Flask Backend Router)
├── Dockerfile                    # Containerization instructions
├── docker-compose.yml            # Multi-container service definitions
├── .env                          # System credentials and variables
├── memory /                      # Core Knowledge Graph Engine
│   ├── direct_neo4j_writer.py    # High-speed sensor storage algorithm (Layer 1)
│   ├── patient_memory.py         # Graphiti management and Neo4j structure module
│   └── graphiti_client.py        # Cloud LLM extraction logic (Ollama Cloud API)
├── insights /                    # Multi-Agent Reporting Logic
│   └── lite_report_agent.py      # CrewAI instructions (Analyst & Writer profiles)
├── templates /                   # Frontend UI Templates
│   └── agentic_interface_enhanced.html # Main Bento UI Dashboard
├── reports /                     # Output directory for AI-generated HTML reports
└── utils /                       # General utilities (e.g., tz_utils.py for timezone sync)
```

---

## Installation & Deployment Guide

The system can be executed locally via a Conda environment or isolated within Docker containers.

### A. Prerequisites
1. Python 3.10+ (Anaconda or Miniconda recommended)
2. Active instances of Neo4j and MongoDB (Local or Cloud)
3. Ollama installed locally (Required if operating localized LLM processing)

### B. Option 1: Conda Environment (Developer Recommendation)

**1. Clone the Repository**
```bash
git clone https://github.com/haraishii/utlmedicore-agentic-ai.git
cd utlmedicore-agentic-ai
```

**2. Setup the Environment**
```bash
conda create -n aisuite-agent python=3.10
conda activate aisuite-agent
pip install -r requirements.txt
```

**3. Configure Environment Variables (.env)**
Ensure an `.env` file is present in the root directory. Use the following template:
```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password

MONGO_URI=mongodb://localhost:27017/

# AI Configuration Mode
GRAPHITI_USE_CLOUD=false
GRAPHITI_LLM_MODEL=llama3.1:8b
# OLLAMA_CLOUD_API_KEY=xxx-xxxxx-xxxx (Required if using Mistral Cloud)
```

**4. Start the Primary Application**
```bash
python agentic_medicore_enhanced.py
```
The application will bind to `http://127.0.0.1:5000` or `http://localhost:5000`.

---

### C. Option 2: Docker Deployment (Preferred for Server Environments)

This method ensures a completely uniform and clean infrastructure, mitigating package conflicts.

```bash
# Ensure the Docker daemon is active
docker-compose up -d --build
```
To monitor the active system logs:
```bash
docker-compose logs -f app
```

---

## Quick Usage Guide

1. **Dashboard Initialization**
   Navigate to `http://localhost:5000`. The upper UI segment displays a "System Diagnostics" panel verifying Neo4j memory stability, MongoDB connections, and LLM node readiness.
2. **Patient Logging (Manual Context)**
   Open a specific patient profile. In the "Manual Data Entry" box, log a simulated event such as:
   - Select Category: Meal
   - Description: "Consumed chicken fried rice"
   - Timestamp: Adjust precisely as needed.
3. **Report Generation**
   Trigger "Generate Report" from the timeline menu (Daily, Weekly, or specific Custom hours). The system processing generally takes between 30 to 90 seconds. Monitor the console terminal for Phase 1 and Phase 2 progression. Upon completion, the clinical report is immediately available for download in HTML format.

---
**Maintained by:** UTLMediCore Architecture Team | Agentic AI Integration
