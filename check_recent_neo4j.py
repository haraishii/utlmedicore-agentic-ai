from neo4j import GraphDatabase

uri = "bolt://localhost:7687"
user = "neo4j"
password = "password"

query = "MATCH (n) RETURN n, labels(n) ORDER BY id(n) DESC LIMIT 5"

try:
    with GraphDatabase.driver(uri, auth=(user, password)) as driver:
        with driver.session() as session:
            result = session.run(query)
            print("--- RECENT NODES IN INDONESIA/TAIPEI ---")
            for record in result:
                node = record[0]
                labels = record[1]
                # Print node properties nicely
                print(f"Labels: {labels}")
                print(f"Data: {dict(node)}")
                print("---")
except Exception as e:
    print("Error querying Neo4j:", e)
