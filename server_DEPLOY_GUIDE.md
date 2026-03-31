# UTLMediCore — Panduan Deploy ke Server Lab

## Konteks Proyek

UTLMediCore adalah sistem **Agentic AI untuk Health Monitoring** berbasis Flask + SocketIO.
Kode utama: `agentic_medicore_enhanced.py`

### Stack Teknologi
- **Backend**: Flask + Flask-SocketIO (port 7000)
- **AI Model**: Ollama (`lfm2.5-thinking:1.2b`) via `aisuite`
- **Database**: MongoDB (sudah jalan di laptop, port 27018)
- **Memory**: Neo4j + Graphiti (`memory/graphiti_client.py`, `memory/patient_memory.py`)
- **Evaluasi**: Opik (`evaluation/opik_integration.py`)
- **Report**: `report_generator.py`

### Konfigurasi Model (dari `AgentConfig`)
```
MONITOR_AGENT    = ollama:lfm2.5-thinking:1.2b
ANALYZER_AGENT   = ollama:lfm2.5-thinking:1.2b
ALERT_AGENT      = ollama:lfm2.5-thinking:1.2b
PREDICTOR_AGENT  = ollama:lfm2.5-thinking:1.2b
COORDINATOR_AGENT= ollama:lfm2.5-thinking:1.2b
```

### Environment Variables yang Dipakai Kode
```
MONGO_URL          → koneksi MongoDB
MONGO_DB_1         → nama database
MONGO_COLLECTION   → nama collection
OLLAMA_HOST        → base URL Ollama
NEO4J_URI          → bolt URI Neo4j
NEO4J_USER         → username Neo4j
NEO4J_PASSWORD     → password Neo4j
FLASK_SECRET_KEY   → secret key Flask
OLLAMA_CLOUD_API_KEY → (opsional) cloud Ollama
```

---

## Kondisi Server Lab

| Item | Detail |
|---|---|
| IP Server | `218.161.3.98` |
| OS | Ubuntu 22.04.2 LTS |
| CPU | Intel i5-8250U, 8 core |
| RAM | 15GB (9GB available) |
| Storage | 468GB (366GB free) |
| GPU | ❌ Tidak ada (CPU only) |
| Docker | ✅ v26.1.2 |
| Docker Compose | ✅ v2.27.0 |
| Akses sudo | ❌ Tidak ada |

### Port yang Sudah Terpakai di Server
| Port | Dipakai |
|---|---|
| 27017 | MongoDB (internal server) |
| 8081 | Gunicorn (project lain) |
| 5050 | Python3 app |
| 7070 | Service lain |
| 80 / 443 | HTTP/HTTPS |
| 22 | SSH |
| 1883 | MQTT |

### Port BEBAS yang Akan Kita Pakai
| Port | Untuk |
|---|---|
| `7000` | Flask App |
| `11434` | Ollama |
| `7474` | Neo4j Browser UI |
| `7687` | Neo4j Bolt |

---

## Arsitektur Deploy

```
💻 Laptop Windows (140.124.134.30)
   └── MongoDB :27018  →  data sensor IoT, sudah berjalan

🖥️ Server Lab (218.161.3.98)
   ├── Flask App :7000      → backend + dashboard (Docker)
   ├── Ollama :11434        → AI model (Docker)
   └── Neo4j :7687          → Graphiti memory (Docker)
```

Flask di server konek ke MongoDB di laptop lewat **SSH Tunnel** karena beda subnet.

---

## Langkah Deploy

### STEP 1 — Upload Project ke Server

Di **PowerShell Windows**:
```powershell
# Buat folder di server
ssh utl@218.161.3.98 "mkdir -p ~/Desktop/medicore"

# Upload semua file project
scp -r C:\path\ke\project\* utl@218.161.3.98:~/Desktop/medicore/
```
> Ganti `C:\path\ke\project\` dengan path project asli kamu

Verifikasi:
```bash
ssh utl@218.161.3.98
cd ~/Desktop/medicore
ls -la
```

---

### STEP 2 — Buat File `.env` di Server

```bash
cd ~/Desktop/medicore
nano .env
```

Isi:
```env
# MongoDB — tetap di laptop, diakses via SSH tunnel
MONGO_URL=mongodb://viewer1:viewer1@127.0.0.1:27018/admin?authSource=admin&directConnection=true
MONGO_DB_1=DCA632971FC3
MONGO_COLLECTION=posture_data

# Ollama — jalan di server Docker
OLLAMA_HOST=http://ollama:11434

# Neo4j — jalan di server Docker
NEO4J_URI=bolt://neo4j:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=medicore2025

# Flask
FLASK_SECRET_KEY=medicore-secret-2025
```

Simpan: `Ctrl+O` → Enter → `Ctrl+X`

---

### STEP 3 — Buat `docker-compose.yml`

```bash
nano ~/Desktop/medicore/docker-compose.yml
```

Isi:
```yaml
version: '3.8'

services:

  ollama:
    image: ollama/ollama:latest
    container_name: medicore_ollama
    restart: unless-stopped
    ports:
      - "11434:11434"
    volumes:
      - ollama_data:/root/.ollama
    environment:
      - OLLAMA_HOST=0.0.0.0
    networks:
      - medicore_net

  neo4j:
    image: neo4j:5.18
    container_name: medicore_neo4j
    restart: unless-stopped
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      NEO4J_AUTH: neo4j/medicore2025
      NEO4J_PLUGINS: '["apoc"]'
      NEO4J_dbms_security_procedures_unrestricted: "apoc.*"
    volumes:
      - neo4j_data:/data
    networks:
      - medicore_net

  medicore_app:
    build:
      context: .
      dockerfile: Dockerfile
    container_name: medicore_backend
    restart: unless-stopped
    ports:
      - "7000:7000"
    depends_on:
      - ollama
      - neo4j
    env_file:
      - .env
    environment:
      OLLAMA_HOST: http://ollama:11434
      NEO4J_URI: bolt://neo4j:7687
    volumes:
      - ./reports:/app/reports
      - ./static:/app/static
    extra_hosts:
      - "host.docker.internal:host-gateway"
    networks:
      - medicore_net

volumes:
  ollama_data:
  neo4j_data:

networks:
  medicore_net:
    driver: bridge
```

---

### STEP 4 — Buat `Dockerfile`

```bash
nano ~/Desktop/medicore/Dockerfile
```

Isi:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y gcc curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p reports/daily reports/weekly reports/monthly reports/archives

EXPOSE 7000

CMD ["python", "agentic_medicore_enhanced.py"]
```

---

### STEP 5 — SSH Tunnel untuk MongoDB

Di **PowerShell Windows** (biarkan tetap terbuka selama server berjalan):
```powershell
ssh -N -L 27018:localhost:27018 utl@218.161.3.98
```

Ini membuat MongoDB laptop bisa diakses dari container di server via `127.0.0.1:27018`.

> ⚠️ Window PowerShell ini jangan ditutup — kalau ditutup, tunnel putus

---

### STEP 6 — Build & Jalankan Docker

Di server:
```bash
cd ~/Desktop/medicore
docker compose up -d --build
```

Cek semua container jalan:
```bash
docker ps
```

---

### STEP 7 — Pull Model Ollama

```bash
docker exec medicore_ollama ollama pull lfm2.5-thinking:1.2b
```

> Ini butuh waktu cukup lama pertama kali (~beberapa menit tergantung koneksi)

Cek model sudah ada:
```bash
docker exec medicore_ollama ollama list
```

---

### STEP 8 — Verifikasi Semua Berjalan

```bash
# Cek semua container
docker ps

# Cek log Flask app
docker logs medicore_backend --tail 50

# Cek log Ollama
docker logs medicore_ollama --tail 20

# Cek Neo4j
docker logs medicore_neo4j --tail 20
```

Akses dashboard dari browser:
```
http://218.161.3.98:7000
```

---

## Troubleshooting Umum

### Flask tidak bisa konek MongoDB
```bash
# Pastikan SSH tunnel aktif di laptop
# Lalu test koneksi dari dalam container
docker exec medicore_backend python -c "from pymongo import MongoClient; c = MongoClient('mongodb://viewer1:viewer1@host.docker.internal:27018/admin?authSource=admin'); print(c.list_database_names())"
```

### Ollama lambat (CPU only)
Normal — server tidak punya GPU. Model `lfm2.5-thinking:1.2b` dipilih karena paling ringan.

### Neo4j gagal start
```bash
docker logs medicore_neo4j
# Biasanya karena RAM kurang — coba restart
docker restart medicore_neo4j
```

### Restart salah satu service
```bash
docker compose restart medicore_app   # restart Flask saja
docker compose restart ollama          # restart Ollama saja
docker compose down                    # stop semua
docker compose up -d                   # start lagi semua
```

---

## Catatan Penting untuk AI yang Membaca Ini

1. **MongoDB tidak di-Dockerkan** — sudah ada di laptop user, diakses via SSH tunnel
2. **`extra_hosts: host.docker.internal`** — ini wajib agar container bisa akses host (laptop via tunnel)
3. **Tidak ada akses sudo** di server — semua harus via Docker, tidak bisa install package langsung
4. **CPU only** — tidak ada GPU, semua inferensi Ollama berjalan di CPU
5. **Port 27018** — MongoDB di laptop menggunakan port non-standard ini (bukan 27017)
6. **`lfm2.5-thinking:1.2b`** — model yang digunakan, hanya ~0.7GB, cocok untuk CPU
