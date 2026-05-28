import numpy as np
import faiss
from database.neo4j_connection import neo4j_conn
from services.embedding_service import create_embedding

_faiss_index = None
_doc_id_map = []
_doc_metadata_map = {}

def reset_faiss_index():
    global _faiss_index, _doc_id_map, _doc_metadata_map
    _faiss_index = None
    _doc_id_map = []
    _doc_metadata_map = {}
    print("FAISS index has been reset")

def get_faiss_index():
    global _faiss_index, _doc_id_map, _doc_metadata_map
    
    if _faiss_index is None or len(_doc_id_map) == 0:
        print("Building FAISS index from Neo4j...")

        
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
            d.embedding AS embedding,
            d.status AS status
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
            
            # Map labels to type
            labels = doc["labels"] or []
            doc_type = "Other"
            if "Book" in labels:
                doc_type = "Book"
            elif "Article" in labels:
                doc_type = "Article"
            elif "Thesis" in labels:
                doc_type = "Thesis"

            # Cache metadata to avoid querying DB for vector results
            _doc_metadata_map[doc["id"]] = {
                "id": doc["id"],
                "title": doc["title"],
                "year": doc["year"],
                "image_url": doc.get("image_url"),
                "authors": doc.get("authors", []),
                "labels": doc["labels"],
                "type": doc_type,
                "status": doc.get("status") or "active",
                "source": "vector"
            }
            embeddings.append(doc["embedding"])
            
        vectors = np.array(embeddings, dtype=np.float32)
        
        # L2 Normalize for Inner Product to act as Cosine Similarity
        faiss.normalize_L2(vectors)
        
        dim = vectors.shape[1]
        _faiss_index = faiss.IndexFlatIP(dim)
        _faiss_index.add(vectors)
        
        print(f"FAISS index built with {len(_doc_id_map)} vectors")

        
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
            
            # Filter out hidden documents if not requested
            if not filters.get("include_hidden", False) and doc_meta.get("status") == "hidden":
                continue
                
            # Filter by type if requested
            if doc_type:
                match = any(label in doc_type for label in doc_meta.get("labels", []))
                if not match:
                    continue
                    
            doc_meta["score"] = score
            doc_meta["priority"] = 50
            results.append(doc_meta)
            
    return results

def get_similar_documents_by_embedding(doc_id, limit=10):
    """Tìm tài liệu tương đồng dựa trên embedding sử dụng FAISS index."""
    index = get_faiss_index()
    if index.ntotal == 0:
        return []

    # 1. Lấy embedding của tài liệu đích từ Neo4j
    cypher = """
    MATCH (d)
    WHERE (d:Book OR d:Article OR d:Thesis) AND d.id = $id
    RETURN d.embedding AS embedding
    """
    res = neo4j_conn.query(cypher, {"id": doc_id})
    if not res or not res[0].get("embedding"):
        return []

    doc_embedding = res[0]["embedding"]
    if doc_embedding is None:
        return []

    query_np = np.array([doc_embedding], dtype=np.float32)
    faiss.normalize_L2(query_np)

    # 2. Tìm kiếm limit + 1 tài liệu gần nhất (vì tài liệu hiện tại sẽ trả về đầu tiên với khoảng cách ~1.0)
    distances, indices = index.search(query_np, limit + 1)

    results = []
    for i, idx in enumerate(indices[0]):
        if idx != -1:
            found_id = _doc_id_map[idx]
            # Loại trừ chính tài liệu đang xem
            if found_id == doc_id:
                continue

            score = float(distances[0][i])
            doc_meta = dict(_doc_metadata_map[found_id])
            
            # Loại trừ tài liệu ẩn
            if doc_meta.get("status") == "hidden":
                continue
                
            doc_meta["score"] = score
            results.append(doc_meta)

    return results[:limit]