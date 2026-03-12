import time
import os
from neo4j import GraphDatabase
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# NEO4J CONFIGURATION
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

def print_header():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=" * 60)
    print("      NEO4J REAL-TIME NODE MONITOR - UTLMediCore")
    print("=" * 60)
    print(f"Connected to: {NEO4J_URI}")
    print(f"Polling every 5 seconds... Press Ctrl+C to stop.")
    print("-" * 60)

def monitor_new_nodes():
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    try:
        while True:
            print_header()
            
            with driver.session() as session:
                # Query for the latest 10 nodes
                # Adjust 'created_at' if your system uses a different property name
                query = """
                MATCH (n)
                RETURN 
                    labels(n) as labels, 
                    n.name as name, 
                    n.uuid as uuid,
                    n.created_at as created_at,
                    id(n) as internal_id,
                    properties(n) as props
                ORDER BY n.created_at DESC, id(n) DESC
                LIMIT 10
                """
                
                results = session.run(query)
                
                print(f"{'INDEX':<6} | {'TIME':<20} | {'LABEL':<15} | {'NAME/ID':<25}")
                print("-" * 60)
                
                found = False
                for i, record in enumerate(results):
                    found = True
                    # Format timestamp
                    ts = record["created_at"]
                    if not ts:
                        ts = "N/A"
                    elif hasattr(ts, 'to_native'): # Neo4j DateTime object
                        ts = ts.to_native().strftime('%Y-%m-%d %H:%M:%S')
                    
                    label = record["labels"][0] if record["labels"] else "No Label"
                    name_id = record["name"] or record["uuid"] or f"ID:{record['internal_id']}"
                    
                    print(f"{i+1:<6} | {str(ts):<20} | {str(label):<15} | {str(name_id):<25}")
                
                if not found:
                    print("No nodes found in the database.")
            
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\nStopping monitor...")
    except Exception as e:
        print(f"\nError: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    monitor_new_nodes()
