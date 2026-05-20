import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from database.neo4j_connection import neo4j_conn

def inspect_db():
    output_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'db_info.txt'))
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("--- 1. SUBJECTS ---\n")
        subjects_query = "MATCH (s:Subject) RETURN s.id AS id, s.name AS name LIMIT 200"
        subjects = neo4j_conn.query(subjects_query)
        f.write(f"Total Subjects found (limited to 200): {len(subjects)}\n")
        for s in subjects[:100]:
            f.write(f"  Subject: ID={s['id']}, Name={s['name']}\n")
        if len(subjects) > 100:
            f.write("  ...\n")

        f.write("\n--- 2. CATEGORIES (LINH VUC) ---\n")
        categories_query = "MATCH (c:Category) RETURN c.id AS id, c.name AS name"
        categories = neo4j_conn.query(categories_query)
        f.write(f"Total Categories found: {len(categories)}\n")
        for c in categories:
            f.write(f"  Category: ID={c['id']}, Name={c['name']}\n")

        f.write("\n--- 3. RELATIONSHIPS BETWEEN SUBJECTS ---\n")
        rel_subjects_query = "MATCH (s1:Subject)-[r:RELATED_TO]->(s2:Subject) RETURN s1.name AS s1_name, s2.name AS s2_name LIMIT 100"
        rels = neo4j_conn.query(rel_subjects_query)
        f.write(f"Total RELATED_TO Subject relationships found (sample 100): {len(rels)}\n")
        for r in rels:
            f.write(f"  ({r['s1_name']}) -[:RELATED_TO]-> ({r['s2_name']})\n")

        f.write("\n--- 4. RELATIONSHIPS BETWEEN SUBJECT & CATEGORY ---\n")
        rel_cat_query = "MATCH (s:Subject)-[r]-(c:Category) RETURN type(r) AS rel_type, s.name AS s_name, c.name AS c_name LIMIT 100"
        cat_rels = neo4j_conn.query(rel_cat_query)
        f.write(f"Total Subject-Category relationships found (sample 100): {len(cat_rels)}\n")
        for r in cat_rels:
            f.write(f"  ({r['s_name']}) -[:{r['rel_type']}]- (Category: {r['c_name']})\n")
            
        f.write("\n--- 5. ALL LABELS IN NEO4J ---\n")
        labels_query = "CALL db.labels() YIELD label RETURN label"
        labels = neo4j_conn.query(labels_query)
        for l in labels:
            f.write(f"  Label: {l['label']}\n")

    print(f"Inspection complete. Output written to {output_path}")

if __name__ == "__main__":
    inspect_db()
