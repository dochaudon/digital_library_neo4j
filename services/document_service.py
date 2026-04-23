from models.document_model import (
    get_all_documents,
    get_document_by_id,
    get_documents_by_type,
    count_documents,
    get_related_documents
)

import uuid
from database.neo4j_connection import neo4j_conn

# 🔥 NEW IMPORT
from services.embedding_service import create_embedding, build_document_text


# =========================
# GET LIST (PAGINATION)
# =========================
def get_documents_service(page=1, limit=20, doc_type=None):
    skip = (page - 1) * limit

    if doc_type:
        return get_documents_by_type(doc_type, skip, limit)

    return get_all_documents(skip, limit)


# =========================
# COUNT
# =========================
def count_documents_service(doc_type=None):
    if not doc_type:
        return count_documents()

    query = """
    MATCH (d)
    WHERE
        ($type = "Book" AND d:Book) OR
        ($type = "Article" AND d:Article) OR
        ($type = "Thesis" AND d:Thesis)
    RETURN count(d) AS total
    """

    result = neo4j_conn.query(query, {"type": doc_type})
    return result[0]["total"] if result else 0


# =========================
# GET DETAIL
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
def get_related_documents_service(doc_id, limit=5):
    return get_related_documents(doc_id, limit)


# =========================
# CREATE DOCUMENT
# =========================
def create_document_service(data):
    doc_id = str(uuid.uuid4())
    doc_type = data.get("type")

    if doc_type not in ["Book", "Article", "Thesis"]:
        return None

    label = doc_type

    # 🔥 EMBEDDING
    doc_text = build_document_text(
        data.get("title"),
        data.get("abstract")
    )
    embedding = create_embedding(doc_text)

    query = f"""
    CREATE (d:{label} {{
        id: $id,
        title: $title,
        year: $year,
        pages: $pages,
        abstract: $abstract,
        file_url: $file_url,
        embedding: $embedding
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
        "embedding": embedding
    }

    neo4j_conn.query(query, params)

    # AUTHOR
    for name in data.get("authors", []):
        neo4j_conn.query("""
        MERGE (a:Author {name:$name})
        WITH a
        MATCH (d {id:$id})
        MERGE (d)-[:HAS_AUTHOR]->(a)
        """, {"name": name.strip(), "id": doc_id})

    # SUBJECT
    for name in data.get("subjects", []):
        neo4j_conn.query("""
        MERGE (s:Subject {name:$name})
        WITH s
        MATCH (d {id:$id})
        MERGE (d)-[:HAS_SUBJECT]->(s)
        """, {"name": name.strip(), "id": doc_id})

    # KEYWORD
    for name in data.get("keywords", []):
        neo4j_conn.query("""
        MERGE (k:Keyword {name:$name})
        WITH k
        MATCH (d {id:$id})
        MERGE (d)-[:HAS_KEYWORD]->(k)
        """, {"name": name.strip(), "id": doc_id})

    return doc_id


# =========================
# UPDATE DOCUMENT
# =========================
def update_document_service(doc_id, data):

    # 🔥 RE-EMBEDDING
    doc_text = build_document_text(
        data.get("title"),
        data.get("abstract")
    )
    embedding = create_embedding(doc_text)

    query = """
    MATCH (d {id:$id})
    SET 
        d.title = $title,
        d.year = $year,
        d.pages = $pages,
        d.abstract = $abstract,
        d.file_url = $file_url,
        d.embedding = $embedding
    RETURN d
    """

    neo4j_conn.query(query, {
        "id": doc_id,
        "title": data.get("title"),
        "year": data.get("year"),
        "pages": data.get("pages"),
        "abstract": data.get("abstract"),
        "file_url": data.get("file_url"),
        "embedding": embedding
    })

    # RESET RELATION
    neo4j_conn.query("""
    MATCH (d {id:$id})-[r:HAS_AUTHOR|HAS_SUBJECT|HAS_KEYWORD]->()
    DELETE r
    """, {"id": doc_id})

    # RE-ADD
    for name in data.get("authors", []):
        neo4j_conn.query("""
        MERGE (a:Author {name:$name})
        WITH a
        MATCH (d {id:$id})
        MERGE (d)-[:HAS_AUTHOR]->(a)
        """, {"name": name.strip(), "id": doc_id})

    for name in data.get("subjects", []):
        neo4j_conn.query("""
        MERGE (s:Subject {name:$name})
        WITH s
        MATCH (d {id:$id})
        MERGE (d)-[:HAS_SUBJECT]->(s)
        """, {"name": name.strip(), "id": doc_id})

    for name in data.get("keywords", []):
        neo4j_conn.query("""
        MERGE (k:Keyword {name:$name})
        WITH k
        MATCH (d {id:$id})
        MERGE (d)-[:HAS_KEYWORD]->(k)
        """, {"name": name.strip(), "id": doc_id})

    return True


# =========================
# DELETE DOCUMENT
# =========================
def delete_document_service(doc_id):
    query = """
    MATCH (d {id:$id})
    DETACH DELETE d
    """
    return neo4j_conn.query(query, {"id": doc_id})