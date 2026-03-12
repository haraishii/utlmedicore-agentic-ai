# UTLMediCore Agentic AI - Healthcare Monitoring System

**Revolutionary AI-powered health monitoring with multi-agent architecture**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Flask-3.0+-green.svg)](https://flask.palletsprojects.com/)
[![AI Model](https://img.shields.io/badge/Model-lfm2.5--thinking:1.2b-orange.svg)](https://ollama.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

> 100% Fall Detection | 90% Accuracy | 9.3s Response Time | 0.7GB Ultra-Efficient Model

---

## Overview

UTLMediCore is an autonomous healthcare monitoring system powered by 5 collaborative AI agents working together to provide real-time patient safety monitoring, pattern detection, and predictive analytics.

After testing 13 different AI models across 246+ test cases, we achieved breakthrough performance with the lfm2.5-thinking:1.2b model.

### Performance Highlights
- **100% Fall Detection Rate** (14/14 falls detected)
- **90% Overall Accuracy** (highest among all tested models)
- **0.903 F1 Score** (best balance of precision and recall)
- **9.3s Average Response Time** (1.5x faster than alternatives)
- **0.7 GB Model Size** (7x smaller than 8B parameter models)
- **100% Reliability** (zero timeouts in testing)

---

## Multi-Agent Architecture

The system employs 5 specialized AI agents that collaborate autonomously:

### 1. Monitor Agent
**Real-time anomaly detection and vital monitoring**
- Continuous sensor data analysis
- Fall detection with 100% accuracy
- Vital signs monitoring (HR, SpO2)
- Contextual risk assessment
- Instant anomaly alerts

### 2. Analyzer Agent
**Deep pattern analysis and trend detection**
- Historical pattern recognition
- Activity distribution analysis
- Location hotspot detection
- Statistical trend analysis
- Risk score calculation

### 3. Alert Agent
**Priority-based alert generation**
- Multi-level severity classification (CRITICAL/WARNING/INFO)
- Actionable recommendation generation
- Automated notification dispatch
- Alert priority management

### 4. Predictor Agent
**Future risk estimation and forecasting**
- Predictive trend analysis
- Future risk forecasting
- Early warning generation
- Preventive recommendations

### 5. Coordinator Agent
**Multi-agent orchestration and decision making**
- Agent workflow coordination
- Comprehensive health summaries
- Natural language report generation
- Autonomous decision making

---

## Key Features

### Real-time Monitoring
- Live sensor data processing (HR, SpO2, Posture, Location, Steps)
- Instant anomaly detection with sub-10s latency
- WebSocket-based live updates
- Real-time activity timeline

### Intelligent Analysis
- Pattern detection from historical data (100+ data points)
- Contextual risk assessment (location + posture + vitals)
- Multi-factor correlation analysis
- Automatic threshold detection

### Predictive Analytics
- Future risk forecasting (next hour)
- Trend prediction with confidence scores
- Early warning system
- Preventive action recommendations

### Autonomous Alerts
- Automatic alert generation with severity classification
- Priority-based notification system
- Recommended actions for medical staff
- Alert history tracking

### Comprehensive Reporting
- Downloadable health reports (HTML/JSON formats)
- Customizable time ranges (1 hour to 1 week)
- Historical data analysis
- AI-generated natural language summaries

### Model Flexibility
- Dynamic model selection per agent
- Real-time model switching via UI
- Support for 13+ Ollama models
- Production-optimized defaults

---

## Revolutionary Model Discovery

We conducted extensive testing of 13 AI models to find the perfect balance of accuracy, speed, and efficiency.

### lfm2.5-thinking:1.2b - The Breakthrough

After comprehensive evaluation, we discovered that this ultra-small 1.2B parameter model outperforms ALL larger models, including 8B parameter alternatives.

#### Comparison Table

| Model | Size | Fall Detection | Accuracy | F1 Score | Latency | Status |
|-------|------|----------------|----------|----------|---------|--------|
| **lfm2.5-thinking:1.2b** | **0.7 GB** | **100%** | **90%** | **0.903** | **9.3s** | **PRODUCTION** |
| llama3.1:8b | 4.9 GB | 92.9% | 73.3% | 0.765 | 14.2s | Previous best |
| medicaldiagnostic:8b | ~5 GB | 71.4% | 76.7% | 0.741 | 13.7s | Medical specialist |
| qwen2.5:7b | ~4 GB | 50% | 70% | 0.609 | 11.8s | Rejected |
| llama3.2:3b | 2.0 GB | 50% | 63.3% | 0.560 | 6.7s | Too small |

#### Why lfm2.5-thinking:1.2b Dominates

**vs llama3.1:8b (Previous Best):**
- **+7.1%** better fall detection (100% vs 92.9%)
- **+16.7%** better accuracy (90% vs 73.3%)
- **+18%** better F1 score (0.903 vs 0.765)
- **34% faster** response (9.3s vs 14.2s)
- **86% smaller** size (0.7 GB vs 4.9 GB)
- **Zero missed falls** (vs 1 missed)

**The Secret: "Thinking" Architecture**
- Specialized for reasoning and pattern recognition
- More efficient parameter usage
- Perfect fit for healthcare diagnostics
- Proves that design matters more than size for AI models

Full Analysis: See [reports/LFM25_THINKING_RESULTS_SHOCKING.md](reports/LFM25_THINKING_RESULTS_SHOCKING.md)

---

## Technology Stack

### Backend
- **Python 3.8+** - Core language
- **Flask 3.0+** - Web framework
- **Flask-SocketIO** - Real-time bidirectional communication
- **MongoDB** - Patient data persistence
- **AISuite** - Universal AI model interface
- **Ollama** - Local LLM inference engine
- **Opik** - Evaluation and tracing framework

### Frontend
- **HTML5/CSS3/JavaScript** - Modern web standards
- **Socket.IO Client** - Real-time updates
- **Glassmorphism UI** - Modern design aesthetic
- **Responsive Design** - Mobile-friendly interface

### AI Models
- **lfm2.5-thinking:1.2b** (Production model)
- Compatible with 13+ Ollama models
- Support for model hot-swapping

---

## Installation and Setup

### Prerequisites

1. **Python 3.8 or higher**
```bash
python --version
```

2. **Ollama** (for AI model inference)
```bash
# Download and install from: https://ollama.com/
# Verify installation:
ollama --version
```

3. **MongoDB** (for data storage)
```bash
# Option 1: Local installation
# Download from: https://www.mongodb.com/try/download/community

# Option 2: Use MongoDB Atlas (cloud)
# Sign up at: https://www.mongodb.com/cloud/atlas
```

### Installation Steps

#### 1. Clone Repository
```bash
git clone https://github.com/haraishii/utlmedicore-agentic-ai.git
cd utlmedicore-agentic-ai
```

#### 2. Create Virtual Environment
```bash
# Create venv
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Setup Environment Variables
```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials
# Add MongoDB connection URL and other settings
```

#### 5. Install AI Model
```bash
# Pull the lfm2.5-thinking model
ollama pull lfm2.5-thinking:1.2b

# Verify installation
ollama list
```

#### 6. Run Application
```bash
python agentic_medicore_enhanced.py
```

#### 7. Access Web Interface
```
http://localhost:5000
```

---

## Usage Guide

### Web Dashboard

The interface is divided into several key sections:

#### 1. Patient Monitoring Grid
- Real-time vital signs display
- Fall detection status
- Risk score visualization
- Patient location tracking
- Activity metrics

#### 2. Autonomous Agents Panel (Left)
- View all 5 AI agents
- Real-time status indicators
- Model configuration
- Agent-specific metrics
- Detailed agent information

#### 3. Active Alerts Panel (Right)
- Live alerts feed
- Severity-based color coding
- Timestamp and patient info
- Recommended actions
- Alert filtering

#### 4. Monitoring Workflow Timeline
- Real-time agent activities
- Coordination flow visualization
- Agent collaboration tracking
- Detailed action logs

### Model Selection

Click the "Models" button to change AI models for each agent:
1. Click "Models" in Agents Panel
2. Select agent to configure
3. Choose model from dropdown
4. Changes apply immediately

### Download Reports

For each patient:
1. Click on patient card
2. Click "Download Report"
3. Select time range (1 hour to 1 week)
4. Choose format (HTML/JSON)
5. Report downloads automatically

---

## API Endpoints

### Patient Data

**Get All Patient States:**
```http
GET /api/patient-states
```

Response:
```json
{
  "device_id": {
    "latest_data": {...},
    "risk_score": 0.23,
    "recent_alerts": 2,
    "patterns": [...]
  }
}
```

### Reports

**Generate Patient Report:**
```http
GET /api/generate-report/{device_id}?hours=24&format=html
```

Parameters:
- `device_id` - Patient/Device ID
- `hours` - Time range (1-168)
- `format` - `html` or `json`

### Agent Configuration

**Get Current Agent Models:**
```http
GET /api/agent-models
```

**Update Agent Model:**
```http
POST /api/agent-models
Content-Type: application/json

{
  "monitor": "ollama:lfm2.5-thinking:1.2b",
  "analyzer": "ollama:llama3.1:8b"
}
```

**Get Available Models:**
```http
GET /api/available-models
```

---

## Project Structure

```
utlmedicore-agentic-ai/
├── agentic_medicore_enhanced.py  # Main application & agents
├── report_generator.py            # Health report generator
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment template
│
├── templates/
│   └── agentic_interface_enhanced.html  # Web interface
│
├── static/
│   └── enhanced-features.js       # Frontend JavaScript
│
├── evaluation/
│   ├── model_comparison.py        # Model testing framework
│   ├── test_datasets.py           # Comprehensive test cases
│   ├── opik_integration.py        # Evaluation tracing
│   └── README.md                  # Evaluation documentation
│
├── reports/                       # Analysis & documentation
│   ├── LFM25_THINKING_RESULTS_SHOCKING.md
│   ├── EXTENDED_TEST_RESULTS_30_CASES.md
│   ├── FINAL_SUMMARY_ALL_11_MODELS.md
│   ├── ULTIMATE_MODEL_COMPARISON.md
│   └── ...
│
└── docs/                          # Additional documentation
    ├── DEPLOYMENT_LFM25_COMPLETE.md
    ├── ENHANCED_LOGGING_SUMMARY.md
    ├── SECURITY_GUIDE.md
    └── README.md
```

---

## Testing and Evaluation

### Comprehensive Testing Framework

We developed a rigorous testing methodology with:

**Test Dataset:** 30 comprehensive scenarios
- 14 Fall cases (True Positives)
- 11 Normal activities (True Negatives)
- 6 Edge cases (challenging scenarios)

**Evaluation Metrics:**
- **Sensitivity** - Fall detection rate (critical)
- **Specificity** - False positive rate
- **Accuracy** - Overall correctness
- **F1 Score** - Balance of precision and recall
- **Latency** - Response time
- **Reliability** - Completion rate (no timeouts)

**Models Tested (13 total):**
1. lfm2.5-thinking:1.2b (Winner)
2. llama3.1:8b
3. llama3.2:3b
4. qwen2.5:7b
5. medicaldiagnostic:latest
6. meditron:7b
7. medllama2:7b
8. medichat:8b
9. gemma3:12b
10. gpt-oss:20b
11. deepseek-r1:8b
12. deepseek-r1:14b
13. olmo-3:7b

**Total Test Runs:** 246+ LLM calls across all models

Detailed Results: See `reports/` directory for comprehensive analysis

---

## Configuration

### Production Configuration

```python
class AgentConfig:
    # AI Models (All using lfm2.5-thinking:1.2b)
    MONITOR_AGENT = os.getenv('MONITOR_AGENT_MODEL', 'ollama:lfm2.5-thinking:1.2b')
    ANALYZER_AGENT = os.getenv('ANALYZER_AGENT_MODEL', 'ollama:lfm2.5-thinking:1.2b')
    ALERT_AGENT = os.getenv('ALERT_AGENT_MODEL', 'ollama:lfm2.5-thinking:1.2b')
    PREDICTOR_AGENT = os.getenv('PREDICTOR_AGENT_MODEL', 'ollama:lfm2.5-thinking:1.2b')
    COORDINATOR_AGENT = os.getenv('COORDINATOR_AGENT_MODEL', 'ollama:lfm2.5-thinking:1.2b')
    
    # Temperature Settings (per agent)
    TEMPERATURES = {
        "monitor": 0.1,      # Deterministic for safety
        "analyzer": 0.2,     # Balanced
        "predictor": 0.2,    # Balanced
        "alert": 0.1,        # Deterministic
        "coordinator": 0.2   # Flexible
    }
    
    # Timeout Settings (optimized for 9.3s latency)
    TIMEOUTS = {
        "monitor": 20,       # Critical path
        "analyzer": 30,      # Analysis work
        "predictor": 30,     # Predictions
        "alert": 15,         # Time-sensitive
        "coordinator": 25    # Coordination
    }
    
    # Clinical Thresholds
    CRITICAL_FALL_THRESHOLD = 0.95
    ABNORMAL_HR_LOW = 45
    ABNORMAL_HR_HIGH = 110
    HYPOXIA_THRESHOLD = 90
```

---

## Security

This project uses environment variables to protect sensitive credentials.

### Setup Security
1. Copy `.env.example` to `.env`
2. Add your MongoDB credentials to `.env`
3. Never commit `.env` to version control

See [SECURITY_GUIDE.md](SECURITY_GUIDE.md) for detailed security configuration.

---

## Roadmap

### Phase 1: Core Enhancements (Q1 2026)
- Enhanced logging with detailed AI reasoning
- Multi-patient simultaneous monitoring
- Advanced visualization dashboards
- Historical trend charts

### Phase 2: Platform Expansion (Q2 2026)
- Mobile app (iOS/Android)
- REST API for third-party integration
- Multi-language support (ID/EN/CN)
- Voice alert system

### Phase 3: Integration (Q3 2026)
- EMR/EHR system integration
- Wearable device support (Apple Watch, Fitbit)
- Cloud deployment options (AWS/Azure/GCP)
- Telemedicine platform integration

### Phase 4: Intelligence (Q4 2026)
- Multi-modal AI (vision + sensor fusion)
- Personalized health models per patient
- Automated intervention suggestions
- Long-term health prediction (weeks/months)

---

## Contributing

We welcome contributions from the community.

### Ways to Contribute
- Report bugs and issues
- Suggest new features
- Improve documentation
- Add more test cases
- Submit code improvements
- Test new AI models

### Contribution Process

1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guide for Python
- Add tests for new features
- Update documentation
- Test with multiple AI models
- Ensure backward compatibility

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

```
MIT License

Copyright (c) 2026 UTLMediCore Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## Acknowledgments

Special thanks to:

- [Ollama](https://ollama.com/) - For providing excellent local LLM infrastructure
- lfm2.5-thinking:1.2b Team - For creating this revolutionary ultra-lightweight model
- Flask and Socket.IO - For real-time web framework capabilities
- MongoDB - For reliable and scalable data storage
- Opik - For evaluation and tracing framework
- Open Source Community - For continuous inspiration and support

---

## Contact and Support

### Project Maintainer
- **GitHub:** [@haraishii](https://github.com/haraishii)
- **Project:** [UTLMediCore Agentic AI](https://github.com/haraishii/utlmedicore-agentic-ai)

### Getting Help
- Check the [Documentation](docs/)
- Open an [Issue](https://github.com/haraishii/utlmedicore-agentic-ai/issues)
- Read the FAQ (coming soon)

---

## Project Statistics

![GitHub Stars](https://img.shields.io/github/stars/haraishii/utlmedicore-agentic-ai?style=social)
![GitHub Forks](https://img.shields.io/github/forks/haraishii/utlmedicore-agentic-ai?style=social)
![GitHub Issues](https://img.shields.io/github/issues/haraishii/utlmedicore-agentic-ai)
![GitHub Pull Requests](https://img.shields.io/github/issues-pr/haraishii/utlmedicore-agentic-ai)
![GitHub Last Commit](https://img.shields.io/github/last-commit/haraishii/utlmedicore-agentic-ai)

---

## Achievements

- 100% Fall Detection - Perfect accuracy in testing
- 13 Models Evaluated - Comprehensive comparison
- 246+ Test Cases - Rigorous validation
- Revolutionary Discovery - Ultra-small model outperforms all
- Production Ready - Deployed and tested

---

<div align="center">

**Built for Healthcare Safety**

*Saving lives through AI innovation*

[Back to Top](#utlmedicore-agentic-ai---healthcare-monitoring-system)

</div>
