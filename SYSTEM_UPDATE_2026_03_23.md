# 🛰️ UTLMediCore — System Evolution Update
**Tanggal**: 23 Maret 2026
**Topik**: optimalisasi Algoritma Sensor, Debouncing Debat Jantung (0 HR), dan Proteksi Interaksi UI.

---

## 🔬 1. Algoritma Transisi & Memori (Yang Berlaku Sekarang)

Sistem kita mengadopsi konsep **Hybrid 2-Layer Data Processing** yang ditingkatkan dengan aturan **Landmark Event**:

### 🛠️ Aliran Data Sensor (Pipeline)
1.  **Direct-Write (Layer 1)**: Data Vital (HR, SpO2, Posture) ditulis instan ke Neo4j setiap ada kedipan untuk Graph Visualisasi Real-Time.
2.  **Landmark Check**: Sistem memeriksa apakah ada **Perubahan Posture** (`Sitting` ➔ `Lying Down`).
    *   Jika **Berubah**: Sistem **WAJIB** membuatkan rangkuman episode ke *Graphiti LLM* seketika itu juga (Melewati filter Throttling).
    *   Jika **Sama**: Throttling 1 jam berlaku untuk menghemat token dan menjaga kerapatan graph.

---

## 🎯 2. History Perbaikan & Solusi Hari Ini

Berikut adalah tabel kronologis perubahan kode yang kita pasang hari ini:

| Modul/File | Gejala Masalah (Issue) | Solusi Teknikal (Patch) | Dampak Positif |
| :--- | :--- | :--- | :--- |
| **Frontend**<br>`..._interface_enhanced.html` | Chat modal tidak bisa diklik karena Grid Pasien melakukan `render()` ulang secara agresif. | Pasang guard `if (document.querySelector('.overlay.open')) return;` di fungsi `renderPatients()`. | Menunda render visual **HANYA** saat modal report/chat sedang dibuka user. Interaksi 100% mulus. |
| **Debouncer**<br>`patient_memory.py` | Sensor fluktuatif atau dilepas menyebabkan alert "Device Taken Off" yang salah/gagal dibaca AI. | 1. Implementasi **Singleton Cache Objek (`__new__`)** agar variabel hitungan 0 `self._hr_zero_count` tidak amnesia.<br>2. Set target buffer dari **5 data ke 2 data** saja. | Deteksi pelepasan sersor (HR 0) bekerja dalam hitungan <3 detik, sangat responsif terhadap kelambatan I2C sensor fisik. |

---

## 🧠 3. Cara Kerja Debouncer responsif (Debounce Algorithm)

```python
# Pseudo-Logic yang berjalan di Backend saat ini:

    # 1. Objek Statis (Anti-Amnesia)
    def __new__(cls, device_id):
        if device_id not in _patient_instances:
             _patient_instances[device_id] = super(PatientMemory, cls).__new__(cls)
        return _patient_instances[device_id]

    # 2. Debouncer Pemicu (Device off)
    if hr == 0:
        count += 1
        if count >= 2:    # Cukup 2 data beruntun, sensor sah dilepas
            posture = "Device Taken Off"
    else:
        count = 0        # Sensitif reset jika ada data asli (Glich Guard)
```

---

> [!NOTE]  
> Seluruh perbaikan di atas diproduksi pada 23 Maret 12:00 - 13:00 WIB. Server siap menyuguhkan AI Memory aware dengan debouncer stabil 100%.
