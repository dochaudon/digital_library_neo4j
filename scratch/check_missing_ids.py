import sys
import os

# Thêm đường dẫn thư mục gốc để import được
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.neo4j_connection import neo4j_conn

def check_missing_ids():
    labels = ["Author", "Subject", "Keyword", "Category", "Language", "Journal", "Publisher", "University"]
    
    print("Checking metadata nodes missing 'id' property in Neo4j:")
    for label in labels:
        q = f"MATCH (n:{label}) WHERE n.id IS NULL RETURN count(n) AS count"
        res = neo4j_conn.query(q)
        count = res[0]["count"] if res else 0
        
        q_total = f"MATCH (n:{label}) RETURN count(n) AS count"
        res_total = neo4j_conn.query(q_total)
        total = res_total[0]["count"] if res_total else 0
        
        print(f"[{label}] Missing ID: {count} / Total: {total}")

if __name__ == "__main__":
    check_missing_ids()
