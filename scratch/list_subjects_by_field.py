import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.neo4j_connection import neo4j_conn

if sys.platform.startswith('win'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

print("[NEO4J] Connecting...")
query = """
MATCH (s:Subject)
RETURN s.field AS field, s.name AS name, s.id AS id
ORDER BY s.field, s.name
"""
results = neo4j_conn.query(query)

by_field = {}
for r in results:
    f = r["field"] or "Uncategorized"
    if f not in by_field:
        by_field[f] = []
    by_field[f].append(f"{r['id']}: {r['name']}")

for field, subs in by_field.items():
    print(f"\n=== FIELD: {field} ({len(subs)} subjects) ===")
    for s in subs[:30]: # print first 30
        print(f"  {s}")
    if len(subs) > 30:
        print(f"  ... and {len(subs) - 30} more")
