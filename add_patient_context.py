import asyncio
import argparse
from datetime import datetime
from memory.patient_memory import PatientMemory

async def add_context(device_id: str, episode_type: str, content: str):
    print(f"\n[+] Inisialisasi Memory Graph untuk Pasien: {device_id}...")
    memory = PatientMemory(device_id)
    
    print(f"\n[+] Menambahkan Data [{episode_type.upper()}] ke Graphiti...")
    print(f"    Konten: {content}")
    
    # Menambahkan data sebagai episode
    await memory.add_episode(
        content=content,
        episode_type=episode_type
    )
    
    print("\n[✔] Data berhasil disimpan ke dalam Graph Memory!")
    print("    AI (LFM/LLM) sekarang dapat membaca dan mempertimbangkan informasi ini")
    print("    saat memberikan rangkuman aktivitas dan rekomendasi kesehatan.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Tambah Data Konteks Pasien (Makanan, Rekam Medis, Aktivitas)")
    parser.add_argument("--device", type=str, default="DCA632971FC3", help="ID Perangkat/Pasien")
    parser.add_argument("--type", type=str, choices=["medical_record", "meal", "activity", "custom"], required=True, help="Jenis data yang dimasukkan")
    parser.add_argument("--content", type=str, required=True, help="Isi teks/deskripsi data")
    
    args = parser.parse_args()
    
    # Jalankan proses async
    asyncio.run(add_context(args.device, args.type, args.content))
