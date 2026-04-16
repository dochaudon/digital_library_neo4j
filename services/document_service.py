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

import uuid
from database.neo4j_connection import neo4j_conn

# =========================
# CREATE DOCUMENT (🔥 CORE)
# =========================
def create_document(data):
    doc_id = str(uuid.uuid4())
    doc_type = data.get("type")

    if doc_type == "Book":
        label = "Book"
    elif doc_type == "Article":
        label = "Article"
    elif doc_type == "Thesis":
        label = "Thesis"
    else:
        return None

    query = f"""
    CREATE (d:{label} {{
        id: $id,
        title: $title,
        year: $year,
        pages: $pages,
        abstract: $abstract,
        file_url: $file_url
    }})
    RETURN d
    """

    params = {
        "id": doc_id,
        "title": data.get("title"),
        "year": data.get("year"),
        "pages": data.get("pages"),
        "abstract": data.get("abstract"),
        "file_url": data.get("file_url"),
    }

    neo4j_conn.query(query, params)

    # 🔥 HANDLE AUTHOR
    authors = data.get("authors", [])
    for name in authors:
        neo4j_conn.query("""
        MERGE (a:Author {name:$name})
        WITH a
        MATCH (d {id:$id})
        MERGE (d)-[:HAS_AUTHOR]->(a)
        """, {"name": name, "id": doc_id})

    return doc_id


# =========================
# UPDATE DOCUMENT
# =========================
def update_document(doc_id, data):
    query = """
    MATCH (d {id:$id})
    SET d.title = $title,
        d.year = $year,
        d.pages = $pages,
        d.abstract = $abstract,
        d.file_url = $file_url
    RETURN d
    """

    neo4j_conn.query(query, {
        "id": doc_id,
        "title": data.get("title"),
        "year": data.get("year"),
        "pages": data.get("pages"),
        "abstract": data.get("abstract"),
        "file_url": data.get("file_url"),
    })

    # 🔥 reset author
    neo4j_conn.query("""
    MATCH (d {id:$id})-[r:HAS_AUTHOR]->()
    DELETE r
    """, {"id": doc_id})

    for name in data.get("authors", []):
        neo4j_conn.query("""
        MERGE (a:Author {name:$name})
        WITH a
        MATCH (d {id:$id})
        MERGE (d)-[:HAS_AUTHOR]->(a)
        """, {"name": name, "id": doc_id})

    return True


# =========================
# DELETE DOCUMENT
# =========================
def delete_document(doc_id):
    query = """
    MATCH (d {id:$id})
    DETACH DELETE d
    """
    return neo4j_conn.query(query, {"id": doc_id})

def get_documents_service(page=1, limit=10):
    skip = (page - 1) * limit
    return get_all_documents(skip, limit)