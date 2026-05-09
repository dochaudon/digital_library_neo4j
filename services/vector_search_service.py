import numpy as np
import faiss
from database.neo4j_connection import neo4j_conn
from services.embedding_service import create_embedding

_faiss_index = None
_doc_id_map = []
_doc_metadata_map = {}

def get_faiss_index():
    global _faiss_index, _doc_id_map, _doc_metadata_map
    
    if _faiss_index is None:
        print("🔄 Building FAISS index from Neo4j...")
        
        # Fetch all documents that have embeddings
        cypher = """
        MATCH (d)
        WHERE (d:Book OR d:Article OR d:Thesis) AND d.embedding IS NOT NULL
        OPTIONAL MATCH (d)-[:HAS_AUTHOR]->(a:Author)
        RETURN
            d.id AS id,
            d.title AS title,
            d.year AS year,
            d.image_url AS image_url,
            labels(d) AS labels,
            collect(DISTINCT a.name) AS authors,
            d.embedding AS embedding
        """
        docs = neo4j_conn.query(cypher)
        
        if not docs:
            print("⚠️ No embeddings found in DB")
            # Create a dummy index with dimension 384 (all-MiniLM-L6-v2)
            _faiss_index = faiss.IndexFlatIP(384)
            return _faiss_index
            
        embeddings = []
        for doc in docs:
            _doc_id_map.append(doc["id"])
            # Cache metadata to avoid querying DB for vector results
            _doc_metadata_map[doc["id"]] = {
                "id": doc["id"],
                "title": doc["title"],
                "year": doc["year"],
                "image_url": doc.get("image_url"),
                "authors": doc.get("authors", []),
                "labels": doc["labels"],
                "source": "vector"
            }
            embeddings.append(doc["embedding"])
            
        vectors = np.array(embeddings, dtype=np.float32)
        
        # L2 Normalize for Inner Product to act as Cosine Similarity
        faiss.normalize_L2(vectors)
        
        dim = vectors.shape[1]
        _faiss_index = faiss.IndexFlatIP(dim)
        _faiss_index.add(vectors)
        
        print(f"✅ FAISS index built with {len(_doc_id_map)} vectors")
        
    return _faiss_index

def vector_search(query, filters=None, limit=20):
    filters = filters or {}
    doc_type = filters.get("doc_type")
    
    # Normalize
    if doc_type and isinstance(doc_type, str):
        doc_type = [doc_type]

    if not query:
        return []
        
    index = get_faiss_index()
    if index.ntotal == 0:
        return []

    # Tạo embedding cho câu truy vấn
    query_vec = create_embedding(query)
    query_np = np.array([query_vec], dtype=np.float32)
    
    # Normalize truy vấn trước khi search (bắt buộc)
    faiss.normalize_L2(query_np)
    
    # Thực hiện search bằng FAISS
    distances, indices = index.search(query_np, limit)
    
    results = []
    for i, idx in enumerate(indices[0]):
        if idx != -1: # -1 là khi không đủ limit kết quả
            doc_id = _doc_id_map[idx]
            score = float(distances[0][i])
            
            doc_meta = dict(_doc_metadata_map[doc_id])
            
            # Filter by type if requested
            if doc_type:
                match = any(label in doc_type for label in doc_meta.get("labels", []))
                if not match:
                    continue
                    
            doc_meta["score"] = score
            results.append(doc_meta)
            
    return results