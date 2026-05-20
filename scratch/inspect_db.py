import os
from database.neo4j_connection import neo4j_conn

def inspect():
    print("=== NODE LABELS AND COUNTS ===")
    label_query = """
    MATCH (n)
    RETURN labels(n) AS labels, count(*) AS count
    """
    labels = neo4j_conn.query(label_query)
    for l in labels:
        print(f"Labels: {l['labels']}, Count: {l['count']}")

    print("\n=== RELATIONSHIP TYPES AND COUNTS ===")
    rel_query = """
    MATCH ()-[r]->()
    RETURN type(r) AS rel_type, count(*) AS count
    """
    rels = neo4j_conn.query(rel_query)
    for r in rels:
        print(f"Type: {r['rel_type']}, Count: {r['count']}")

    print("\n=== RELATIONSHIP DETAILS BETWEEN DOCUMENTS ===")
    doc_rel_query = """
    MATCH (d1)-[r]->(d2)
    WHERE (d1:Book OR d1:Article OR d1:Thesis) AND (d2:Book OR d2:Article OR d2:Thesis)
    RETURN type(r) AS rel_type, count(*) AS count
    """
    doc_rels = neo4j_conn.query(doc_rel_query)
    for dr in doc_rels:
        print(f"Doc-to-Doc Relation: {dr['rel_type']}, Count: {dr['count']}")

if __name__ == "__main__":
    inspect()
