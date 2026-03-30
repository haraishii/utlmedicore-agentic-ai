import pymongo
from datetime import datetime

url = "mongodb://viewer1:viewer1@127.0.0.1:27018/admin?authSource=admin&directConnection=true"
client = pymongo.MongoClient(url, serverSelectionTimeoutMS=5000)

# Receiver dca63283f618 biasanya nama database-nya sama
db_name = "DCA63283F618"
db = client[db_name]
col = db["posture_data"]

print(f"Checking Database: {db_name}")

try:
    # Agregasi untuk melihat safe_Mac unik, count, dan timestamp awal-akhir
    pipeline = [
        {"$group": {
            "_id": "$safe_Mac",
            "first_seen": {"$min": "$timestamp"},
            "last_seen": {"$max": "$timestamp"},
            "count": {"$sum": 1}
        }}
    ]

    results = list(col.aggregate(pipeline))
    print(f"\n ditemukan {len(results)} node unik:")
    print("-" * 80)
    for r in results:
        m_id = r['_id'] or "Unknown"
        count = r['count']
        first = r['first_seen']
        last = r['last_seen']
        print(f"Device: {m_id:15} | Records: {count:5} | Awal: {first} | Akhir: {last}")
    print("-" * 80)

except Exception as e:
    print(f"Error query: {e}")

client.close()
