import sys
import os

# Add project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.neo4j_connection import neo4j_conn
from services.embedding_service import create_embedding, build_document_text
from services.vector_search_service import reset_faiss_index
from tqdm import tqdm

def rebuild_embeddings():
    print("Starting Rebuild Embeddings Script")

    # Fetch all documents with subjects and keywords
    cypher_fetch = """
    MATCH (d)
    WHERE d:Book OR d:Article OR d:Thesis
    OPTIONAL MATCH (d)-[:HAS_SUBJECT]->(s:Subject)
    OPTIONAL MATCH (d)-[:HAS_KEYWORD]->(k:Keyword)
    RETURN d.id AS id, 
           d.title AS title, 
           d.abstract AS abstract,
           collect(distinct s.name) AS subjects,
           collect(distinct k.name) AS keywords
    """
    docs = neo4j_conn.query(cypher_fetch)
    print(f"Found {len(docs)} documents to update.")
    
    cypher_update = """
    MATCH (d {id: $id})
    SET d.embedding = $embedding
    """
    
    updated_count = 0
    for doc in tqdm(docs, desc="Updating embeddings"):
        text = build_document_text(
            title=doc.get("title"),
            abstract=doc.get("abstract"),
            subjects=doc.get("subjects"),
            keywords=doc.get("keywords")
        )
        embedding = create_embedding(text)
        
        if embedding:
            neo4j_conn.query(cypher_update, {
                "id": doc["id"],
                "embedding": embedding
            })
            updated_count += 1
            
    print(f"Successfully updated {updated_count} documents.")
    
    # Reset FAISS index so it will be rebuilt on the next query
    reset_faiss_index()


if __name__ == "__main__":
    rebuild_embeddings()
