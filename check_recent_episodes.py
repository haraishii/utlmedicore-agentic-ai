from neo4j import GraphDatabase
import os

uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
user = os.getenv("NEO4J_USER", "neo4j")
pw = os.getenv("NEO4J_PASSWORD", "password")

driver = GraphDatabase.driver(uri, auth=(user, pw))

with driver.session() as s:
    r = s.run("MATCH (n:Episodic) WHERE n.group_id='patient_C5945F0F59FB_D612D9000180' RETURN n.name, n.content ORDER BY n.created_at DESC LIMIT 15")
    for rec in r:
        print(f"Name: {rec['n.name']}")
        print(f"Content: {rec['n.content'][:80]}")
        print("-------")

driver.close()
