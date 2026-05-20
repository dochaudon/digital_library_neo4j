import os
import sys

# Reconfigure stdout to support Vietnamese on Windows console
if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.neo4j_connection import neo4j_conn

def inspect_rels():
    print("--- 1. CLASSIFICATION COUNTS BY FIELD ---")
    query = """
    MATCH (f:Field)
    OPTIONAL MATCH (s:Subject)-[:BELONGS_TO]->(f)
    RETURN f.name AS field_name, count(s) AS subject_count
    ORDER BY subject_count DESC
    """
    res = neo4j_conn.query(query)
    for r in res:
        print(f"  Field: {r['field_name']} -> {r['subject_count']} subjects")

    query_uncat = "MATCH (s:Subject) WHERE s.field IS NULL RETURN count(s) AS uncat_count"
    res_uncat = neo4j_conn.query(query_uncat)
    print(f"  Uncategorized subjects: {res_uncat[0]['uncat_count']}")

    print("\n--- 2. LOGICAL SUBJECT-SUBJECT RELATIONSHIPS ---")
    query_rels = """
    MATCH (s1:Subject)-[r:RELATED_TO]->(s2:Subject)
    RETURN count(r) AS rel_count
    """
    res_rels = neo4j_conn.query(query_rels)
    print(f"  Total RELATED_TO relationships now: {res_rels[0]['rel_count']}")

    print("\n--- 3. SAMPLE LOGICAL RELATIONSHIPS ---")
    query_sample = """
    MATCH (s1:Subject)-[r:RELATED_TO]->(s2:Subject)
    RETURN s1.name AS s1_name, s1.field AS s1_field, s2.name AS s2_name, s2.field AS s2_field
    LIMIT 20
    """
    res_sample = neo4j_conn.query(query_sample)
    for r in res_sample:
        print(f"  [{r['s1_field']}] ({r['s1_name']}) -[:RELATED_TO]-> ({r['s2_name']})")

if __name__ == "__main__":
    inspect_rels()
