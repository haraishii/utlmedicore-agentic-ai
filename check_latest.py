from neo4j import GraphDatabase
from datetime import datetime, timezone

uri = "bolt://localhost:7687"
user = "neo4j"
password = "password"

query = """
MATCH (n:Episodic)
RETURN n.name, n.created_at
ORDER BY n.created_at DESC
LIMIT 3
"""

try:
    with GraphDatabase.driver(uri, auth=(user, password)) as driver:
        with driver.session() as session:
            now_utc = datetime.now(timezone.utc)
            now_taipei = now_utc.utctimetuple()
            print(f"[CHECK] Sekarang UTC: {now_utc.strftime('%H:%M:%S')}")
            result = session.run(query)
            rows = list(result)
            if not rows:
                print("  Tidak ada node Episodic sama sekali!")
            for r in rows:
                name = r[0]
                ca   = r[1]  # neo4j DateTime already UTC
                print(f"  name     : {name}")
                print(f"  created  : {ca} UTC")
                print("  ---")
except Exception as e:
    print("Error:", e)
