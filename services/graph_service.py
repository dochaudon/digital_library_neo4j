from models.graph_model import (
    get_book_graph_data,
    get_article_graph_data,
    get_thesis_graph_data
)


# =========================
# MAIN GRAPH SERVICE
# =========================
def get_graph_data(doc_type, document_id):

    if not doc_type or not document_id:
        return {"nodes": [], "edges": []}

    # Normalize type (tránh lỗi input)
    doc_type = doc_type.strip()

    if doc_type == "Book":
        return get_book_graph_data(document_id)

    elif doc_type == "Article":
        return get_article_graph_data(document_id)

    elif doc_type == "Thesis":
        return get_thesis_graph_data(document_id)

    # fallback
    return {"nodes": [], "edges": []}


# =========================
# OPTIONAL: AUTO DETECT TYPE
# =========================
def get_graph_auto(document_id):

    """
    Dùng khi bạn không biết trước loại document
    (tìm trong cả 3 loại)
    """

    # thử từng loại
    book = get_book_graph_data(document_id)
    if book["nodes"]:
        return book

    article = get_article_graph_data(document_id)
    if article["nodes"]:
        return article

    thesis = get_thesis_graph_data(document_id)
    if thesis["nodes"]:
        return thesis

    return {"nodes": [], "edges": []}