import pymongo

try:
    client = pymongo.MongoClient("mongodb://127.0.0.1:27018/")
    
    print("=== MONGODB STRUCTURE VERIFICATION ===")
    dbs = client.list_database_names()
    print(f"Databases found: {dbs}")
    
    target_dbs = ['DCA632971FC3', 'DCA63283F618']
    for db_name in target_dbs:
        if db_name in dbs:
            db = client[db_name]
            print(f"\n--- Database: {db_name} ---")
            collections = db.list_collection_names()
            print(f"Collections: {collections}")
            for coll_name in collections:
                count = db[coll_name].count_documents({})
                print(f"  Collection [{coll_name}] has {count} documents")
                if count > 0:
                    sample = db[coll_name].find_one()
                    # Just print keys to see fields
                    print(f"  Sample Keys: {list(sample.keys())}")
        else:
            print(f"\n--- Database: {db_name} NOT found ---")

except Exception as e:
    print(f"Error checking MongoDB: {e}")
