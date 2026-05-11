import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.neo4j_connection import neo4j_conn
from services.embedding_service import create_embedding, build_document_text
from tqdm import tqdm

def rebuild_embeddings():
    print("Starting Rebuild Embeddings Script")

    
    # Fetch all documents
    cypher_fetch = """
    MATCH (d)
    WHERE d:Book OR d:Article OR d:Thesis
    RETURN d.id AS id, d.title AS title, d.abstract AS abstract
    """
    docs = neo4j_conn.query(cypher_fetch)
    print(f"Found {len(docs)} documents to update.")
    
    cypher_update = """
    MATCH (d {id: $id})
    SET d.embedding = $embedding
    """
    
    updated_count = 0
    for doc in tqdm(docs, desc="Updating embeddings"):
        text = build_document_text(doc.get("title"), doc.get("abstract"))
        embedding = create_embedding(text)
        
        if embedding:
            neo4j_conn.query(cypher_update, {
                "id": doc["id"],
                "embedding": embedding
            })
            updated_count += 1
            
    print(f"Successfully updated {updated_count} documents.")


if __name__ == "__main__":
    rebuild_embeddings()
