from models.graph_model import (
    get_book_graph_data,
    get_article_graph_data,
    get_thesis_graph_data
)


# =========================
# MAP TYPE → FUNCTION
# =========================
GRAPH_FUNCTIONS = {
    "book": get_book_graph_data,
    "article": get_article_graph_data,
    "thesis": get_thesis_graph_data
}


# =========================
# MAIN GRAPH SERVICE
# =========================
def get_graph_data(doc_type, document_id):

    if not doc_type or not document_id:
        return {"nodes": [], "edges": []}

    # normalize input
    doc_type = doc_type.strip().lower()

    graph_func = GRAPH_FUNCTIONS.get(doc_type)

    if not graph_func:
        return {"nodes": [], "edges": []}

    try:
        return graph_func(document_id)
    except Exception:
        return {"nodes": [], "edges": []}


# =========================
# AUTO DETECT TYPE
# =========================
def get_graph_auto(document_id):

    if not document_id:
        return {"nodes": [], "edges": []}

    for func in GRAPH_FUNCTIONS.values():
        try:
            result = func(document_id)
            if result.get("nodes"):
                return result
        except Exception:
            continue

    return {"nodes": [], "edges": []}