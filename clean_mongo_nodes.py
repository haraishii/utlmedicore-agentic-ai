import pymongo

url = "mongodb://viewer1:viewer1@127.0.0.1:27018/admin?authSource=admin&directConnection=true"
client = pymongo.MongoClient(url)

db_name = "DCA63283F618"
db = client[db_name]
col = db["posture_data"]

print(f"Mengakses Database untuk Pembersihan: {db_name}")

try:
    # Kita hapus semua device KECUALI device utama Anda
    target_clean = [
        "202030057004", "19004400D101", "202020057005", "302010057004",
        "C0112003F00D", "8011D00AE008", "600FAFFF600E", "1E8DC2801129", "0C5945F0F59F"
    ]
    
    # query delete
    result = col.delete_many({"safe_Mac": {"$in": target_clean}})
    print(f"✅ Sukses Menghapus {result.deleted_count} record sampah dari database.")

except Exception as e:
    print(f"❌ Error Delete: {e}")

client.close()
