from models.document_model import (
    get_all_documents,
    get_document_by_id,
    get_documents_by_type,
    count_documents,
    get_related_documents
)


# =========================
# GET DOCUMENT LIST (PAGINATION)
# =========================
def get_documents_service(page=1, limit=20):
    skip = (page - 1) * limit
    return get_all_documents(skip, limit)


# =========================
# COUNT DOCUMENTS
# =========================
def count_documents_service():
    return count_documents()


# =========================
# GET DOCUMENT DETAIL
# =========================
def get_document_detail_service(doc_id):
    return get_document_by_id(doc_id)


# =========================
# FILTER BY TYPE
# =========================
def get_documents_by_type_service(doc_type, page=1, limit=20):
    skip = (page - 1) * limit
    return get_documents_by_type(doc_type, skip, limit)


# =========================
# RELATED DOCUMENTS
# =========================
def get_related_documents_service(doc_id, limit=10):
    return get_related_documents(doc_id, limit)