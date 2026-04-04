from models.search_model import search_documents_fulltext
from models.graph_search_model import graph_search


# =========================
# HYBRID SEARCH
# =========================
def hybrid_search(query, filters=None, limit=20):

    if not query and not filters:
        return []

    filters = filters or {}

    # ===== 1. FULLTEXT =====
    fulltext_results = []
    if query:
        fulltext_results = search_documents_fulltext(query, limit)

    # ===== 2. GRAPH =====
    graph_results = []
    if filters:
        graph_results = graph_search(filters, limit)

    # ===== 3. MERGE =====
    combined = fulltext_results + graph_results

    # ===== 4. REMOVE DUPLICATE =====
    seen = set()
    unique_results = []

    for item in combined:
        doc_id = item.get("id")
        if doc_id not in seen:
            seen.add(doc_id)
            unique_results.append(item)

    # ===== 5. NORMALIZE SCORE =====
    for item in unique_results:
        score = item.get("relevance_score", 0)

        # boost graph result
        if item.get("source") == "graph":
            score += 1.5

        # boost exact match title
        if query and query.lower() in item.get("title", "").lower():
            score += 2

        item["final_score"] = score

    # ===== 6. SORT =====
    unique_results.sort(
        key=lambda x: x.get("final_score", 0),
        reverse=True
    )

    return unique_results[:limit]


# =========================
# SMART SEARCH (NLP nhẹ)
# =========================
def smart_search(query, limit=20):

    query_lower = query.lower()

    filters = {}

    # detect author
    if "tác giả" in query_lower:
        filters["author"] = query.replace("tác giả", "").strip()

    # detect subject
    elif "chủ đề" in query_lower:
        filters["subject"] = query.replace("chủ đề", "").strip()

    # detect university
    elif "trường" in query_lower:
        filters["university"] = query.replace("trường", "").strip()

    # detect year
    elif query_lower.isdigit():
        filters["year"] = int(query_lower)

    # ===== fallback =====
    return hybrid_search(query, filters, limit)