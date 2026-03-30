from neo4j import GraphDatabase
import os

uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
user = os.getenv("NEO4J_USER", "neo4j")
pw = os.getenv("NEO4J_PASSWORD", "password")

driver = GraphDatabase.driver(uri, auth=(user, pw))

with driver.session() as s:
    r = s.run("MATCH (n:Episodic) RETURN n LIMIT 5")
    print("Episodic Nodes:")
    for rec in r:
        node = rec['n']
        print(f"ID: {node.id}, Labels: {node.labels}")
        print(f"Properties: {dict(node.items())}\n")

driver.close()
