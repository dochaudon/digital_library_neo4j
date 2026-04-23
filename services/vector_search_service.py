import numpy as np
from database.neo4j_connection import neo4j_conn
from services.embedding_service import create_embedding


# =========================
# COSINE SIMILARITY
# =========================
def cosine_similarity(a, b):
    a = np.array(a)
    b = np.array(b)

    if len(a) == 0 or len(b) == 0:
        return 0

    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))


# =========================
# VECTOR SEARCH
# =========================
def vector_search(query, limit=20):

    # 🔥 tạo embedding cho query
    query_vec = create_embedding(query)

    # 🔥 lấy tất cả document có embedding
    cypher = """
    MATCH (d)
    WHERE (d:Book OR d:Article OR d:Thesis)
      AND d.embedding IS NOT NULL

    RETURN
        d.id AS id,
        d.title AS title,
        d.year AS year,
        d.embedding AS embedding
    """

    docs = neo4j_conn.query(cypher)

    results = []

    for doc in docs:
        score = cosine_similarity(query_vec, doc["embedding"])

        results.append({
            "id": doc["id"],
            "title": doc["title"],
            "year": doc["year"],
            "score": float(score),
            "source": "vector"
        })

    # 🔥 sort theo similarity
    results.sort(key=lambda x: x["score"], reverse=True)

    return results[:limit]