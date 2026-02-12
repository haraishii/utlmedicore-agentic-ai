# ⚡ QUICK START GUIDE - Agentic AI Implementation

**Waktu setup: 15 menit** ⏱️

---

## 🎯 TL;DR - Apa yang Akan Anda Dapatkan

```
SEBELUM:
❌ User harus bertanya manual
❌ Tidak ada monitoring otomatis
❌ Tidak ada alert system
❌ Single AI model

SESUDAH:
✅ Autonomous 24/7 monitoring
✅ Real-time alert notifications
✅ 5 AI agents bekerja parallel
✅ Predictive analytics
```

---

## 📦 Step 1: Install Dependencies (3 menit)

### A. Install Ollama
```bash
# Linux
curl -fsSL https://ollama.com/install.sh | sh

# macOS
brew install ollama

# Windows
# Download dari ollama.com
```

### B. Install Python Packages
```bash
pip install Flask Flask-SocketIO aisuite pymongo numpy
```

### C. Pull AI Models
```bash
# Model utama (WAJIB)
ollama pull llama3.1:8b    # Monitor Agent (1.9 GB)
ollama pull qwen2.5:7b     # Analyzer & Coordinator (4.1 GB)

# Model optional
ollama pull deepseek-r1:8b # Alert Agent (4.7 GB)
ollama pull meditron:7b    # Predictor Agent (3.8 GB)
```

**Estimated download**: ~15 GB total (tergantung koneksi)

---

## 🔧 Step 2: Setup Files (2 menit)

### A. Download Files Agentic AI

Anda perlu 3 file utama:
1. `agentic_medicore.py` - Backend server
2. `templates/agentic_interface.html` - Frontend UI
3. `requirements.txt` - Dependencies list

### B. Konfigurasi MongoDB

Edit `agentic_medicore.py`, line 50-54:

```python
class AgentConfig:
    MONGO_URL = 'mongodb://USER:PASS@HOST:PORT/'  # ⬅️ GANTI INI
    DB_LIST = ['DATABASE1', 'DATABASE2']            # ⬅️ GANTI INI
    COLLECTION_NAME = 'posture_data'                # Nama collection
```

**Contoh**:
```python
MONGO_URL = 'mongodb://utl:2041$$@218.161.3.98:27017/'
DB_LIST = ['DCA632971FC3', '2CCF6754457F']
```

---

## 🚀 Step 3: Run Server (1 menit)

```bash
# Pastikan Ollama running
ollama serve &

# Start Agentic AI
python3 agentic_medicore.py
```

**Expected output**:
```
🚀 UTLMediCore Agentic AI System Starting...
🤖 Autonomous Agents: Monitor, Analyzer, Alert, Predictor, Coordinator
📊 Auto-analysis interval: 30s
🔔 Auto-alerts: Enabled
📡 MongoDB Listener Started for 2 databases
🤖 Autonomous Monitor Agent Started
 * Running on http://0.0.0.0:5000
```

---

## 🌐 Step 4: Access UI (1 menit)

1. Buka browser: `http://localhost:5000`
2. Anda akan melihat:
   - ✅ 5 Agent cards di kiri (status IDLE)
   - ✅ Patient monitoring grid di tengah
   - ✅ Real-time alerts panel di kanan

**First load**: "Waiting for patient data..."

---

## 🧪 Step 5: Test System (5 menit)

### Test 1: Verify Agents Running
Check terminal output:
```
[AGENT] DCA632971FC3: NORMAL
.................  ⬅️ Heartbeat dots setiap 1 detik
```

### Test 2: Simulate Data
Insert test data ke MongoDB:
```javascript
// Di MongoDB Compass atau mongosh
db.posture_data.insertOne({
  device_ID: "TEST123",
  Posture_state: 5,  // ⚠️ Fall!
  Area: 6,           // Bathroom
  HR: 95,
  Blood_oxygen: 92,
  timestamp: new Date()
})
```

### Test 3: Check Alert
Dalam **3 detik**, Anda akan melihat:
1. ✅ Agent "Monitor" berubah ACTIVE (hijau)
2. ✅ Alert muncul di panel kanan (merah)
3. ✅ Message: "🚨 CRITICAL ALERT: FALL_DETECTED"
4. ✅ Sound notification

### Test 4: Manual Analysis
1. Klik patient card
2. Atau klik button "Force Analysis"
3. Lihat AI summary di bawah

---

## 🔍 Step 6: Monitoring & Troubleshooting

### Check System Health

#### MongoDB Connection
```bash
python3 -c "from pymongo import MongoClient; print(MongoClient('YOUR_MONGO_URL').admin.command('ismaster'))"
```

#### Ollama Models
```bash
ollama list
```

Expected:
```
NAME              SIZE
llama3.1:8b      1.9 GB
qwen2.5:7b       4.1 GB
```

#### Agent Status
Check browser console (F12):
```javascript
// Should see:
✅ Connected to Agentic AI Backend
```

### Common Issues

#### "Model not found"
```bash
# Pull missing model
ollama pull llama3.1:8b
```

#### "MongoDB connection failed"
- Verify URL, username, password
- Check firewall: MongoDB port (27017) open?
- Test with mongosh: `mongosh "YOUR_MONGO_URL"`

#### "No patient data"
- Wait 30s for first analysis cycle
- Check MongoDB: `db.posture_data.find().limit(1)`
- Insert test data (see Test 2 above)

#### "WebSocket not connecting"
- Check Flask-SocketIO installed: `pip show Flask-SocketIO`
- Disable browser extensions (ad blockers)
- Try incognito mode

---

## 🎛️ Step 7: Customize Settings

### Change Analysis Interval
Edit `agentic_medicore.py`, line 59:
```python
AUTO_ANALYSIS_INTERVAL = 30  # 30s → change to 10s untuk faster
```

### Change Alert Thresholds
Edit `agentic_medicore.py`, line 54-57:
```python
ABNORMAL_HR_LOW = 45    # Bradycardia
ABNORMAL_HR_HIGH = 110  # Tachycardia
HYPOXIA_THRESHOLD = 90  # SpO2 critical
```

### Disable Auto-Alerts (Testing Mode)
Edit `agentic_medicore.py`, line 61:
```python
AUTO_ALERT_ENABLED = False  # No auto-alerts
```

### Change AI Models
Edit `agentic_medicore.py`, line 45-49:
```python
MONITOR_AGENT = "ollama:llama3.1:8b"     # Fast detection
ANALYZER_AGENT = "ollama:qwen2.5:7b"     # Pattern analysis
ALERT_AGENT = "ollama:deepseek-r1:8b"    # Emergency logic
PREDICTOR_AGENT = "ollama:meditron:7b"   # Medical expertise
COORDINATOR_AGENT = "ollama:qwen2.5:7b"  # Orchestration
```

---

## 🔄 Step 8: Integration dengan Sistem Lama

### Option A: Run Both Systems
```bash
# Terminal 1: IMU Dashboard (existing)
node server.js  # Port 3000

# Terminal 2: Agentic AI (new)
python3 agentic_medicore.py  # Port 5000
```

Akses:
- Dashboard: http://localhost:3000
- Agentic AI: http://localhost:5000

### Option B: Use Only Agentic AI
```bash
# Stop server.js
# Run only:
python3 agentic_medicore.py
```

**Note**: Agentic AI langsung baca dari MongoDB, jadi `server.js` optional.

---

## 📊 Step 9: Understand the Dashboard

### Left Panel: AI Agents
```
🤖 Monitor Agent
   - Status: IDLE / ACTIVE / PROCESSING
   - Metrics: Checks, Anomalies detected
   
🤖 Analyzer Agent
   - Metrics: Patterns found
   
🤖 Alert Agent
   - Metrics: Active alerts count
   
🤖 Predictor Agent
   - Metrics: Predictions made
   
🤖 Coordinator Agent
   - Metrics: Coordinations performed
```

### Center Panel: Patient Monitoring
```
📊 Patient Cards:
   - Device ID (e.g., DCA632971FC3)
   - Risk meter (color-coded: green → yellow → red)
   - Data points count
   - Click → Manual analysis
   
🧠 Autonomous Analysis:
   - AI-generated summary
   - Raw data (JSON)
   - Timestamp
```

### Right Panel: Real-time Alerts
```
🚨 Alert Items:
   - CRITICAL (red) = Immediate action
   - WARNING (yellow) = Monitor closely
   - Time of occurrence
   - Recommended actions
   
   Example:
   🚨 CRITICAL
   FALL_DETECTED in Bathroom
   → Dispatch emergency response
   → Check for head injury
```

---

## 🎯 Step 10: Real-world Usage

### Scenario 1: Fall Detection
```
TIMELINE:
15:00:00 - Patient falls (Posture_state = 5)
15:00:01 - MongoDB listener detects new data
15:00:02 - Monitor Agent: "FALL DETECTED"
15:00:03 - Alert Agent: Create CRITICAL alert
15:00:03 - WebSocket broadcast to all clients
15:00:03 - UI shows red alert + sound
15:00:05 - Coordinator generates full analysis
```

### Scenario 2: Vital Sign Monitoring
```
Patient HR increasing: 75 → 85 → 95 → 105 → 115

Analyzer Agent detects trend: "deteriorating"
Predictor Agent forecasts: "Next hour risk: 0.73"
Alert Agent generates: "WARNING: Tachycardia trend"
UI shows: Yellow warning panel
```

### Scenario 3: Pattern Detection
```
Analyzer Agent finds:
- Patient sitting 45% of time
- Most active in Living Room
- Average HR: 78 bpm
- 2 falls in last 7 days

Coordinator summary:
"Patient shows increased fall risk.
Recommend mobility assessment and
environmental safety review."
```

---

## 🚀 Next Steps

### Level 1: Basic Usage ✅
- [x] System running
- [x] Monitoring active patients
- [x] Receiving alerts

### Level 2: Customization
- [ ] Tune alert thresholds
- [ ] Add custom analysis rules
- [ ] Configure notification channels (email/SMS)

### Level 3: Advanced
- [ ] Multi-user authentication
- [ ] Historical data playback
- [ ] Custom ML models
- [ ] API integration dengan EHR systems

---

## 📞 Support & Resources

### Documentation
- **Full docs**: `AGENTIC_AI_DOCUMENTATION.md`
- **Architecture**: `ARCHITECTURE_DIAGRAMS.md`
- **Comparison**: `COMPARISON_BEFORE_AFTER.md`

### Troubleshooting
1. Check terminal logs
2. Verify MongoDB connection
3. Test Ollama: `ollama run llama3.1:8b "Hello"`
4. Browser console (F12) for WebSocket errors

### Community
- GitHub Issues: Report bugs
- Email: support@utlmedicore.com (example)
- Documentation: Built-in help in UI

---

## ✅ Success Checklist

Before going live, verify:
- [ ] MongoDB connection stable
- [ ] Ollama models downloaded
- [ ] Agents showing IDLE status
- [ ] Patient data appearing in UI
- [ ] Alerts working (test with fall simulation)
- [ ] WebSocket connected (green dot in header)
- [ ] Analysis generates AI summary

---

## 🎉 Congratulations!

Anda sekarang memiliki **Autonomous Health Monitoring System** dengan:
- ✅ 24/7 monitoring
- ✅ Real-time alerts
- ✅ Multi-agent AI
- ✅ Predictive analytics

**Total setup time**: ~15 minutes
**Result**: Production-ready agentic AI system! 🚀

---

**Siap deploy? Lihat production deployment guide di dokumentasi lengkap!**
