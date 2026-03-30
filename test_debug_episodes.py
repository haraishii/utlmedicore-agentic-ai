"""Check Episodic data with correct group_id."""
import os
from neo4j import GraphDatabase

uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
pw = os.getenv("NEO4J_PASSWORD", "password")
driver = GraphDatabase.driver(uri, auth=("neo4j", pw))

gid = "patient_C5945F0F59FB_D612D9000180"

with driver.session() as s:
    # Count and date range
    r = s.run(
        "MATCH (e:Episodic) WHERE e.group_id = $gid RETURN count(e) AS c, min(e.created_at) AS earliest, max(e.created_at) AS latest",
        gid=gid
    )
    rec = r.single()
    print(f"Episodic count: {rec['c']}")
    print(f"Earliest: {rec['earliest']}")
    print(f"Latest: {rec['latest']}")
    
    # Sample content
    r2 = s.run(
        """
        MATCH (e:Episodic)
        WHERE e.group_id = $gid
          AND e.created_at >= datetime() - duration('PT24H')
        RETURN e.content AS content, e.name AS name, toString(e.created_at) AS ts
        ORDER BY e.created_at DESC
        LIMIT 5
        """,
        gid=gid
    )
    print("\n--- Last 5 Episodic entries (24h) ---")
    for rec in r2:
        print(f"[{rec['ts'][:19]}] {rec['name']}")
        content = rec['content'] or ''
        print(f"  {content[:200]}")
        # Check if Activity/Posture and Location are parseable
        has_posture = "Activity/Posture:" in content
        has_location = "Location:" in content
        print(f"  has_posture={has_posture}, has_location={has_location}")
        print()

driver.close()
