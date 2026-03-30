from neo4j import GraphDatabase
import os

uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
user = os.getenv("NEO4J_USER", "neo4j")
pw = os.getenv("NEO4J_PASSWORD", "password")

driver = GraphDatabase.driver(uri, auth=(user, pw))

with driver.session() as s:
    r2 = s.run("MATCH (n:Episodic) WHERE n.name STARTS WITH 'meal' OR n.name STARTS WITH 'activity' OR n.name STARTS WITH 'medical' RETURN n LIMIT 10")
    print("\nManual Context Nodes:")
    for rec in r2:
        node = rec['n']
        print(f"Name: {node['name']}, Content: {node['content']}")

driver.close()
