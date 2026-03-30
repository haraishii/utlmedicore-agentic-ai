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

## Apa itu UTLMediCore?
**UTLMediCore Agentic AI** adalah sebuah sistem pemantauan kesehatan cerdas dan penghasil laporan medis berbasis kecerdasan buatan (AI). Sistem ini dirancang untuk menghubungkan data sensor waktu-nyata (seperti Detak Jantung, SpO2, dan Postur) dengan konteks manual dari pasien (seperti jadwal makan, durasi tidur, dan aktivitas harian) menjadi laporan klinis terpadu yang sangat presisi.

Aplikasi ini tidak hanya merekam data secara pasif, melainkan menggunakan mesin **Knowledge Graph (Neo4j)** dan pendekatan **Multi-Agent (CrewAI / Lite Agent)** untuk mensintesis pola dan memberikan wawasan/rekomendasi medis secara otomatis.

---

## Fitur Utama
1. **Agentic Insight Generator**: Menggunakan Multi-Phase Cognitive Reasoning untuk membuat laporan medis harian atau kustom (1 jam - 168 jam).
   - Phase 1 (Analyst): Mencari korelasi antara aktivitas/makan dengan fluktuasi tanda-tanda vital.
   - Phase 2 (Clinical Writer): Menyusun wawasan tersebut menggunakan bahasa medis profesional bebas-emoticon.
2. **Hybrid Graph-Memory Engine**: Menyimpan struktur data interaktif dengan Neo4j + Graphiti AI.
   - Direct Database Write untuk penyimpanan sensor mentah super cepat (< 1 detik).
   - Entity Extraction LLM untuk membaca konteks log manual dan mengubahnya menjadi relasi logis di dalam graf.
3. **Cloud & Local LLM Ready**: Integrasi mulus menggunakan Ollama antara pemrosesan LLM lokal (llama3.1:8b) bebas biaya, atau pengalihan ke Cloud API (mistral-large-3:675b / kimi-k2-thinking) untuk penalaran (reasoning) yang berat.
4. **Manual Context Entry**: Antarmuka responsif bagi pengguna untuk mencatat rekaman makanan, aktivitas, dan riwayat kesehatan. Semua catatan dikalibrasi secara ketat ke zona waktu referensi lokal (UTC+8).
5. **Bento Dashboard UI**: Antarmuka modern untuk memantau status sistem, koneksi database MongoDB/Neo4j, dan mengunduh laporan berformat HTML.

---

## Arsitektur Sistem & Cara Kerjanya

1. **Frontend (Bento Dashboard)**
   Berbasis HTML/CSS/JS (Flask Templates). Menyajikan formulir untuk menambahkan Manual Context (Makanan/Peristiwa), serta tombol pemicu yang mengaktifkan pembuatan laporan AI.
2. **Backend (Python / Flask)**
   agentic_medicore_enhanced.py bertindak sebagai router utama yang mengatur jalurnya data antara Frontend, sistem memori (Neo4j), dan sistem Agen (CrewAI).
3. **Database Layer**
   - MongoDB: Untuk menyimpan raw log data/tangkapan log IoT.
   - Neo4j: Database graf (Knowledge Graph) yang bertugas menghubungkan entitas. Contohnya: (Pasien)-[:HAD_READING]->(Detak Jantung) disilangkan dengan (Pasien)-[:CONSUMED]->(Makanan Pedas).
4. **Agent Layer (CrewAI / Lite Agent)**
   Saat user meminta laporan, Agent akan menarik seluruh memory/graph dari Neo4j. AI mengevaluasi data, mendeteksi anomali, dan menulis laporan medis.

---

## Struktur Direktori Utama

```text
utlmedicore-agentic-ai/
├── agentic_medicore_enhanced.py  # MAIN APP (Flask Backend Router)
├── Dockerfile                    # Konfigurasi container untuk isolasi
├── docker-compose.yml            # Konfigurasi layanan multi-container (DB & App)
├── .env                          # Konfigurasi kredensial sistem (API Key, DB passwords)
├── memory /                      # Core Knowledge Graph Engine
│   ├── direct_neo4j_writer.py    # Algoritma penyimpanan sensor tanpa batas (layer 1)
│   ├── patient_memory.py         # Modul utama manajemen Graphiti dan struktur Neo4j
│   └── graphiti_client.py        # Ekstraksi LLM ke Cloud (Ollama Cloud API)
├── insights /                    # Logika Multi-Agent & Report
│   └── lite_report_agent.py      # Skrip instruksi untuk CrewAI (Analyst + Writer)
├── templates /                   # UI Frontend HTML
│   └── agentic_interface_enhanced.html # Bento Dashboard utama
├── reports /                     # Direktori laporan otomatis (Daily / Custom)
└── utils /                       # Modul general (tz_utils.py untuk sinkronisasi waktu)
```

---

## Instalasi & Persiapan Menjalankan Sistem

Sistem ini bisa dijalankan langsung di local environment (Conda) atau menggunakan Docker.

### A. Syarat Sistem Utama (Prerequisites)
1. Python 3.10+ (atau Anaconda/Miniconda)
2. Instance Neo4j dan MongoDB yang sedang berjalan (di lokal maupun di cloud terpisah).
3. Ollama diinstal lokal jika Anda merencanakan pemrosesan LLM di mesin lokal.

### B. Opsi 1: Menjalankan Menggunakan Conda (Rekomendasi Developer)

**1. Clone Repositori**
```bash
git clone https://github.com/haraishii/utlmedicore-agentic-ai.git
cd utlmedicore-agentic-ai
```

**2. Atur Conda Environment**
```bash
conda create -n aisuite-agent python=3.10
conda activate aisuite-agent
pip install -r requirements.txt
```

**3. Konfigurasi Lingkungan (.env)**
Buat atau pastikan keberadaan file .env di root dan sesuaikan dengan contoh environment ini:
```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password_anda

MONGO_URI=mongodb://localhost:27017/

# Mode Penggunaan AI
GRAPHITI_USE_CLOUD=false
GRAPHITI_LLM_MODEL=llama3.1:8b
# OLLAMA_CLOUD_API_KEY=xxx-xxxxx-xxxx (Jika menggunakan Mistral Cloud)
```

**4. Jalankan Aplikasi Utama**
```bash
python agentic_medicore_enhanced.py
```
Aplikasi akan aktif di http://127.0.0.1:5000 atau http://localhost:5000.

---

### C. Opsi 2: Menjalankan Menggunakan Docker (Deployment/Server)

Cara ini sangat direkomendasikan jika Anda ingin agar infrastruktur benar-benar seragam dan bersih di laptop/server tanpa benturan versi package.

```bash
# Pastikan Docker Desktop / Daemon Anda berjalan
docker-compose up -d --build
```
Log sistem bisa Anda amati dengan menjalankan perintah:
```bash
docker-compose logs -f app
```

---

## Panduan Penggunaan Singkat

1. **Dashboard**
   Buka http://localhost:5000. Di bagian atas, antarmuka akan menampilkan "System Diagnostics" yang mengecek kesiapan Memori Neo4j, MongoDB, dan LLM Routing.
2. **Log Pasien (Manual Context)**
   Buka salah satu profil pasien. Di boks "Manual Data Entry", coba catat aktivitas simulasi seperti:
   - Pilih kategori: Meal
   - Ketik: "Makan nasi goreng"
   - Atur Jam: Sesuai keperluan.
3. **Generate Report**
   Pilih "Generate Report" di menu periode (Harian, Mingguan, atau Kustom jam tertentu). Sistem akan berpikir selama 30 - 90 detik. Tunggu terminal memproses fasa (Phase 1 & Phase 2). Jika laporan selesai, ia dapat segera diunduh dalam bentuk ekstensi HTML.
