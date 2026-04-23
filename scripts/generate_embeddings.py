from database.neo4j_connection import neo4j_conn
from services.embedding_service import create_embedding, build_document_text

def run():
    query = """
    MATCH (d)
    WHERE d:Book OR d:Article OR d:Thesis
    RETURN d.id AS id, d.title AS title, d.abstract AS abstract
    """

    docs = neo4j_conn.query(query)

    for doc in docs:
        text = build_document_text(doc["title"], doc["abstract"])
        embedding = create_embedding(text)

        neo4j_conn.query("""
        MATCH (d {id: $id})
        SET d.embedding = $embedding
        """, {
            "id": doc["id"],
            "embedding": embedding
        })

        print(f"Updated embedding for: {doc['title']}")

if __name__ == "__main__":
    run()