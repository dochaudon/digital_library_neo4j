import sys
import os

# Allow running from project root
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database.neo4j_connection import neo4j_conn
from services.embedding_service import create_embedding, build_document_text


def run():
    # Fix for Windows console encoding
    import sys
    if sys.platform == "win32":
        sys.stdout.reconfigure(encoding='utf-8')

    # Fix #4: Fetch richer context — subjects, keywords, categories
    query = """
    MATCH (d)
    WHERE d:Book OR d:Article OR d:Thesis

    OPTIONAL MATCH (d)-[:HAS_SUBJECT]->(s:Subject)
    OPTIONAL MATCH (d)-[:HAS_KEYWORD]->(k:Keyword)
    OPTIONAL MATCH (d)-[:HAS_CATEGORY]->(c:Category)

    RETURN
        d.id       AS id,
        d.title    AS title,
        d.abstract AS abstract,
        collect(DISTINCT s.name) AS subjects,
        collect(DISTINCT k.name) AS keywords,
        collect(DISTINCT c.name) AS categories
    """

    docs = neo4j_conn.query(query)
    total = len(docs)
    print(f"Found {total} documents to embed")

    for i, doc in enumerate(docs, 1):
        text = build_document_text(
            title=doc["title"],
            abstract=doc["abstract"],
            subjects=doc.get("subjects"),
            keywords=doc.get("keywords"),
            categories=doc.get("categories")
        )
        embedding = create_embedding(text)

        neo4j_conn.query("""
        MATCH (d {id: $id})
        SET d.embedding = $embedding
        """, {
            "id": doc["id"],
            "embedding": embedding
        })

        print(f"[{i}/{total}] OK: {doc['title']}")

    print("All embeddings updated!")


if __name__ == "__main__":
    run()