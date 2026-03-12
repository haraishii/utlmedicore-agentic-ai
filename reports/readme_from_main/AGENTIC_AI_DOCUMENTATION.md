# UTLMediCore - Agentic AI Health Monitoring System
## 🚀 Implementasi Autonomous Multi-Agent Architecture

---

## 📋 DAFTAR ISI
1. [Arsitektur System](#arsitektur-system)
2. [Fitur Agentic AI](#fitur-agentic-ai)
3. [Instalasi & Setup](#instalasi--setup)
4. [Cara Kerja Agents](#cara-kerja-agents)
5. [Integrasi dengan Sistem Existing](#integrasi-sistem-existing)
6. [API Documentation](#api-documentation)
7. [Troubleshooting](#troubleshooting)

---

## 🏗️ ARSITEKTUR SYSTEM

### Before (Manual System)
```
User → Chat Input → AI Model → Response
         ↑
    Manual Data Fetching
```

### After (Agentic AI System)
```
MongoDB ──→ MonitorAgent ──→ AnalyzerAgent ──→ CoordinatorAgent ──→ Auto Actions
    ↓           ↓                 ↓                    ↓                    ↓
  Live      Anomaly           Pattern            Multi-Agent         Alerts
  Data      Detection         Analysis          Orchestration      + Predictions
    ↓           ↓                 ↓                    ↓
  Patient ──→ AlertAgent ──→ PredictorAgent ──→ WebSocket ──→ Real-time UI
  State      Generation        Forecasting           Emit
```

---

## 🤖 FITUR AGENTIC AI

### 1. **Monitor Agent** (Real-time Anomaly Detection)
- ✅ **Autonomous Operation**: Berjalan setiap 30 detik tanpa trigger manual
- ✅ **Instant Detection**: 
  - Fall detection (Posture_state = 5)
  - Bradycardia (HR < 45 bpm)
  - Tachycardia (HR > 110 bpm)
  - Hypoxia (SpO2 < 90%)
  - Contextual risk (e.g., lying in bathroom)
- ✅ **Output**: Anomaly reports dengan severity level

**Kode Utama**:
```python
class MonitorAgent:
    @staticmethod
    def analyze_realtime(patient_state):
        # Deteksi jatuh otomatis
        if posture_val == 5:
            anomalies.append("FALL_DETECTED")
            severity = "CRITICAL"
```

### 2. **Analyzer Agent** (Pattern Detection)
- ✅ **Statistical Analysis**:
  - Activity distribution (% waktu per postur)
  - Vital signs trends (mean, std, range)
  - Location hotspots (area paling sering)
- ✅ **Risk Scoring**: Menghitung risk score 0-1
- ✅ **Output**: Pattern insights untuk decision making

**Contoh Output**:
```json
{
  "activity_distribution": {
    "Sitting": "45.2%",
    "Walking": "30.1%",
    "Lying Down": "24.7%"
  },
  "vitals_trend": {
    "hr_avg": 78.5,
    "hr_std": 12.3,
    "spo2_avg": 96.2
  },
  "risk_assessment": 0.35
}
```

### 3. **Alert Agent** (Intelligent Prioritization)
- ✅ **Auto-Alert Creation**: Langsung generate alert saat anomaly terdeteksi
- ✅ **Severity Classification**: CRITICAL / WARNING / INFO
- ✅ **Action Suggestions**: Memberikan rekomendasi tindakan
- ✅ **WebSocket Broadcasting**: Push alerts ke semua clients

**Contoh Alert**:
```json
{
  "id": "ALERT_1738234567",
  "severity": "CRITICAL",
  "message": "🚨 CRITICAL ALERT: FALL_DETECTED",
  "actions_required": [
    "Dispatch emergency response immediately",
    "Check for head injury or fracture"
  ],
  "auto_notify": true
}
```

### 4. **Predictor Agent** (Future Risk Estimation)
- ✅ **Trend Detection**: Improving / Stable / Deteriorating
- ✅ **Short-term Risk**: Estimasi risiko 1 jam ke depan
- ✅ **Preventive Recommendations**: Saran sebelum masalah terjadi

**Contoh Prediction**:
```json
{
  "next_hour_risk": 0.73,
  "trend_direction": "deteriorating",
  "recommendations": [
    "Increase monitoring frequency",
    "Consider preventive intervention"
  ]
}
```

### 5. **Coordinator Agent** (Multi-Agent Orchestration)
- ✅ **Centralized Control**: Mengkoordinasi semua agents
- ✅ **AI Summary Generation**: Menggunakan LLM untuk generate natural language summary
- ✅ **Decision Making**: Menentukan kapan harus trigger emergency protocol

**Flow Coordination**:
```
1. Terima data baru dari MongoDB
2. Trigger MonitorAgent → Deteksi anomaly
3. Jika anomaly: Trigger AlertAgent → Create alert
4. Trigger AnalyzerAgent → Analyze patterns
5. Trigger PredictorAgent → Predict future risk
6. Generate AI summary menggunakan LLM
7. Broadcast hasil ke WebSocket clients
```

---

## ⚙️ INSTALASI & SETUP

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Install Ollama Models
```bash
# Install Ollama terlebih dahulu dari ollama.ai

# Pull required models
ollama pull llama3.1:8b
ollama pull qwen2.5:7b
ollama pull deepseek-r1:8b
ollama pull meditron:7b
```

### Step 3: Konfigurasi MongoDB
Edit `agentic_medicore.py`:
```python
class AgentConfig:
    MONGO_URL = 'mongodb://utl:2041$$@218.161.3.98:27017/'  # Ganti dengan URL Anda
    DB_LIST = ['DCA632971FC3', '2CCF6754457F']  # Database yang di-monitor
```

### Step 4: Jalankan Server
```bash
python agentic_medicore.py
```

Output expected:
```
🚀 UTLMediCore Agentic AI System Starting...
🤖 Autonomous Agents: Monitor, Analyzer, Alert, Predictor, Coordinator
📊 Auto-analysis interval: 30s
🔔 Auto-alerts: Enabled
📡 MongoDB Listener Started for 2 databases
🤖 Autonomous Monitor Agent Started
```

### Step 5: Akses Interface
Buka browser: `http://localhost:5000`

---

## 🔄 CARA KERJA AGENTS

### Autonomous Loop (Background Thread)
```python
def autonomous_monitor_loop():
    while True:
        for device_id, patient_state in PATIENT_STATES.items():
            # 1. Run coordinated analysis
            results = CoordinatorAgent.coordinate_analysis(device_id)
            
            # 2. Auto-generate alerts if critical
            if results['monitoring'] and results['monitoring']['severity'] == 'CRITICAL':
                alert = AlertAgent.create_alert(results['monitoring'])
                socketio.emit('ai_alert', alert)
        
        time.sleep(30)  # Wait 30 seconds
```

### MongoDB Listener (Real-time Data Ingestion)
```python
def mongodb_listener():
    while True:
        # 1. Fetch new documents from MongoDB
        new_docs = collection.find({'_id': {'$gt': last_id}})
        
        for doc in new_docs:
            # 2. Update patient state
            device_id = doc.get('device_ID')
            PATIENT_STATES[device_id].add_data(doc)
            
            # 3. Emit to frontend
            socketio.emit('sensor_update', doc)
        
        time.sleep(1)  # Check every second
```

---

## 🔌 INTEGRASI DENGAN SISTEM EXISTING

### Integrasi dengan IMU Dashboard (server.js)
Tidak perlu mengubah `server.js` yang sudah ada. Agentic AI berjalan paralel:

```
server.js (Port 3000)        agentic_medicore.py (Port 5000)
      ↓                                   ↓
  MongoDB ←─────────────────────────→ MongoDB
      ↓                                   ↓
  Socket.IO                          Socket.IO
      ↓                                   ↓
imuhtmll.html                  agentic_interface.html
```

### Migrasi dari app.py Lama
File `app.py` lama masih bisa digunakan untuk chat interface. Agentic system menambahkan:
1. ✅ Autonomous monitoring (tidak ada di app.py lama)
2. ✅ Multi-agent architecture (app.py hanya single model)
3. ✅ Real-time WebSocket (app.py hanya HTTP request/response)
4. ✅ Predictive analytics (app.py hanya reactive)

### Menggunakan Kedua System
```bash
# Terminal 1: IMU Dashboard Backend
node server.js

# Terminal 2: Agentic AI Backend
python agentic_medicore.py

# Terminal 3: Original Chat Backend (optional)
python app.py
```

Akses:
- IMU Dashboard: http://localhost:3000
- Agentic AI: http://localhost:5000
- Original Chat: http://localhost:5000 (jika running app.py)

---

## 📡 API DOCUMENTATION

### WebSocket Events

#### Client → Server
```javascript
// Request manual analysis
socket.emit('request_analysis', {
  device_id: 'DCA632971FC3'
});
```

#### Server → Client
```javascript
// 1. Patient state update
socket.on('patient_states', (states) => {
  // states = { device_id: { risk_score, data_points, ... } }
});

// 2. Real-time sensor update
socket.on('sensor_update', (data) => {
  // data = { device_id, data: { HR, SpO2, Posture_state, ... } }
});

// 3. Autonomous alert
socket.on('ai_alert', (alert) => {
  // alert = { id, severity, message, actions_required, ... }
});

// 4. Analysis result
socket.on('analysis_result', (data) => {
  // data = { results: {...}, summary: "..." }
});
```

### HTTP Endpoints

#### GET `/api/patient-states`
Get current state of all monitored patients.

**Response**:
```json
{
  "DCA632971FC3": {
    "device_id": "DCA632971FC3",
    "risk_score": 0.42,
    "data_points": 1523,
    "last_update": "2025-01-30T15:23:45",
    "patterns": []
  }
}
```

#### GET `/api/active-alerts`
Get last 20 active alerts.

**Response**:
```json
[
  {
    "id": "ALERT_1738234567",
    "timestamp": "2025-01-30T15:20:00",
    "device_id": "DCA632971FC3",
    "severity": "CRITICAL",
    "message": "🚨 CRITICAL ALERT: FALL_DETECTED",
    "actions_required": [...]
  }
]
```

#### POST `/api/force-analysis/<device_id>`
Manually trigger comprehensive analysis for a specific device.

**Response**:
```json
{
  "results": {
    "monitoring": {...},
    "patterns": {...},
    "prediction": {...}
  },
  "ai_summary": "Patient shows stable vital signs..."
}
```

#### POST `/ask`
Chat with AI (enhanced with agentic context).

**Request**:
```json
{
  "question": "What's the patient status?",
  "model": "ollama:qwen2.5:7b"
}
```

**Response**:
```json
{
  "answer": "Based on autonomous monitoring...",
  "category": "agentic-analysis"
}
```

---

## 🎯 KONFIGURASI THRESHOLDS

Edit `AgentConfig` untuk customize:

```python
class AgentConfig:
    # Alert Thresholds
    CRITICAL_FALL_THRESHOLD = 0.95  # 95% confidence untuk fall
    ABNORMAL_HR_LOW = 45            # Bradycardia threshold
    ABNORMAL_HR_HIGH = 110          # Tachycardia threshold
    HYPOXIA_THRESHOLD = 90          # SpO2 critical level
    
    # Autonomous Behavior
    AUTO_ALERT_ENABLED = True                # Enable auto-alerts
    AUTO_ANALYSIS_INTERVAL = 30              # Analysis frequency (seconds)
    PATTERN_DETECTION_WINDOW = 100           # Data points to analyze
    
    # Models per Agent
    MONITOR_AGENT = "ollama:llama3.1:8b"     # Fast, efficient
    ANALYZER_AGENT = "ollama:qwen2.5:7b"     # Analytical
    ALERT_AGENT = "ollama:deepseek-r1:8b"    # Emergency logic
    PREDICTOR_AGENT = "ollama:meditron:7b"   # Medical expertise
    COORDINATOR_AGENT = "ollama:qwen2.5:7b"  # Orchestration
```

---

## 🐛 TROUBLESHOOTING

### Problem: Agents tidak berjalan
**Symptom**: Console tidak ada output "🤖 Autonomous Monitor Agent Started"

**Solution**:
```python
# Check background thread status
import threading
print(threading.enumerate())  # Should show autonomous threads
```

### Problem: MongoDB connection failed
**Symptom**: `[MONGODB ERROR] Authentication failed`

**Solution**:
1. Verify credentials di `AgentConfig.MONGO_URL`
2. Test connection:
```bash
mongosh "mongodb://utl:2041$$@218.161.3.98:27017/"
```

### Problem: Ollama model tidak ditemukan
**Symptom**: `Model 'ollama:llama3.1:8b' not found`

**Solution**:
```bash
# List installed models
ollama list

# Pull missing model
ollama pull llama3.1:8b
```

### Problem: WebSocket tidak connect
**Symptom**: Browser console error "Failed to connect to ws://"

**Solution**:
1. Check Flask-SocketIO running:
```python
# Di agentic_medicore.py
socketio.run(app, host='0.0.0.0', port=5000, debug=True)
```

2. Allow CORS:
```python
socketio = SocketIO(app, cors_allowed_origins="*")
```

### Problem: No alerts generated
**Symptom**: System running tapi tidak ada alerts

**Solution**:
1. Check AUTO_ALERT_ENABLED = True
2. Verify data masuk:
```python
print(f"Patient states: {len(PATIENT_STATES)}")
print(f"History length: {len(PATIENT_STATES[device_id].history)}")
```

3. Lower thresholds untuk testing:
```python
ABNORMAL_HR_HIGH = 100  # Lebih sensitif
```

---

## 📊 MONITORING & LOGGING

### Enable Verbose Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Di autonomous_monitor_loop()
print(f"[AGENT] Processing {device_id}: {len(patient_state.history)} points")
```

### Performance Metrics
```python
# Tambahkan di CoordinatorAgent
import time

start = time.time()
results = CoordinatorAgent.coordinate_analysis(device_id)
elapsed = time.time() - start

print(f"Analysis completed in {elapsed:.2f}s")
```

---

## 🚀 PRODUCTION DEPLOYMENT

### Using Gunicorn
```bash
gunicorn --worker-class eventlet -w 1 agentic_medicore:app --bind 0.0.0.0:5000
```

### Using Docker
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["python", "agentic_medicore.py"]
```

### Environment Variables
```bash
export MONGO_URL="mongodb://user:pass@host:port/"
export AUTO_ANALYSIS_INTERVAL=30
export OLLAMA_HOST="http://localhost:11434"
```

---

## 📝 NEXT STEPS

### Fitur Tambahan yang Bisa Dikembangkan
1. ✅ **Multi-user Support**: Auth & authorization per device
2. ✅ **Historical Playback**: Replay data history
3. ✅ **Custom Alerts**: User-defined thresholds
4. ✅ **Email/SMS Notifications**: External alert delivery
5. ✅ **Dashboard Analytics**: Grafik risk trends
6. ✅ **Machine Learning**: Train custom anomaly detection models
7. ✅ **API Gateway**: Rate limiting, authentication
8. ✅ **Mobile App**: React Native integration

---

## 📞 SUPPORT

Jika ada pertanyaan atau issue:
1. Check troubleshooting section
2. Review console logs
3. Test individual agents manually
4. Verify MongoDB connection
5. Check Ollama model availability

---

**Created by**: UTL Team  
**Version**: 1.0.0  
**Last Updated**: January 2025  
**License**: MIT

---

## 🎓 KESIMPULAN

Sistem Agentic AI ini memberikan:
- ✅ **Autonomous**: Berjalan tanpa intervensi manual
- ✅ **Proactive**: Deteksi masalah sebelum critical
- ✅ **Intelligent**: Multi-agent collaboration
- ✅ **Real-time**: WebSocket untuk instant updates
- ✅ **Scalable**: Bisa monitor multiple patients

Upgrade dari manual chat → autonomous intelligent system! 🚀
