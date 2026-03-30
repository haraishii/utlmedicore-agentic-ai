
import asyncio
import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

# Load credentials from .env
load_dotenv('e:/agentic/.env')

NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

DEVICE_ID = "C5945F0F59FB_D612D9000180"
GROUP_ID = f"patient_{DEVICE_ID}"

def check_graph_data():
    print(f"--- Diagnostik Graph Memory Pasien: {DEVICE_ID} ---")
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    with driver.session() as session:
        # 1. Cek total episode yang tersimpan
        count_query = "MATCH (e:Episodic) WHERE e.group_id = $gid RETURN count(e) as total"
        result = session.run(count_query, gid=GROUP_ID)
        total = result.single()["total"]
        print(f"Total Episode di Graph: {total}")
        
        if total == 0:
            print("Peringatan: Belum ada data tersimpan di Graph untuk pasien ini.")
            print("Solusi: Biarkan simulator berjalan sampai mencapai 50 data points.")
            return

        # 2. Ambil 5 data terbaru
        latest_query = """
        MATCH (e:Episodic) 
        WHERE e.group_id = $gid 
        RETURN e.content as content, e.created_at as time
        ORDER BY e.created_at DESC 
        LIMIT 5
        """
        results = session.run(latest_query, gid=GROUP_ID)
        
        print("\n5 Data Terakhir di Memori:")
        print("-" * 50)
        has_calorie = False
        for record in results:
            content = record["content"]
            time = record["time"]
            print(f"[{time}] {content[:150]}...")
            if "Kcal" in content:
                has_calorie = True
        print("-" * 50)
        
        if has_calorie:
            print("\nSUKSES: Data kalori DITEMUKAN di dalam memori Graph.")
        else:
            print("\nBELUM DITEMUKAN: Data kalori tidak ada di 5 memori terakhir.")
            print("Kemungkinan data ini adalah 'data lama' sebelum upgrade kode tadi pagi.")

    driver.close()

if __name__ == "__main__":
    try:
        check_graph_data()
    except Exception as e:
        print(f"Error Koneksi: {e}")
