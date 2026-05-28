from models.document_model import (
    get_all_documents,
    get_document_by_id,
    get_documents_by_type,
    count_documents,
    get_related_documents,
    get_related_documents_by_author  # 🔥 RE-ADD
)

import uuid
from database.neo4j_connection import neo4j_conn

# 🔥 NEW IMPORT
from services.embedding_service import create_embedding, build_document_text
from services.vector_search_service import reset_faiss_index



# =========================
# GET LIST (PAGINATION)
# =========================
def get_documents_service(page=1, limit=20, doc_type=None, q=None, include_hidden=False):
    if doc_type and isinstance(doc_type, str):
        doc_type = [doc_type]
        
    skip = (page - 1) * limit

    if doc_type:
        return get_documents_by_type(doc_type, skip, limit, include_hidden)

    return get_all_documents(skip, limit, q, include_hidden)


# =========================
# COUNT
# =========================
def count_documents_service(doc_type=None, q=None, include_hidden=False):
    if doc_type and isinstance(doc_type, str):
        doc_type = [doc_type]
        
    if not doc_type:
        return count_documents(q, include_hidden)

    query = """
    MATCH (d)
    WHERE ($type IS NULL OR ANY(label IN labels(d) WHERE label IN $type))
      AND ($include_hidden OR d.status IS NULL OR d.status = 'active')
    RETURN count(d) AS total
    """

    result = neo4j_conn.query(query, {"type": doc_type, "include_hidden": include_hidden})
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

def get_related_documents_by_author_service(doc_id, limit=10):  # 🔥 RE-ADD
    return get_related_documents_by_author(doc_id, limit)

def get_similar_documents_service(doc_id, limit=10):
    """Tìm tài liệu tương tự dựa trên FAISS embedding. Nếu không tìm thấy, dự phòng bằng Graph."""
    from services.vector_search_service import get_similar_documents_by_embedding
    similar = get_similar_documents_by_embedding(doc_id, limit)
    if not similar:
        # Dự phòng bằng cách lấy tài liệu cùng chủ đề/từ khóa từ Graph DB
        return get_related_documents_service(doc_id, limit)
    return similar

def get_semantic_recommendations_service(doc_id, limit=10):
    """Tìm kiếm đề xuất dựa trên vector embedding (Semantic Search)"""
    from services.vector_search_service import get_similar_documents_by_embedding
    return get_similar_documents_by_embedding(doc_id, limit)


# =========================
# =========================
# HELPER FOR AUTO-INCREMENT METADATA ID
# =========================
def ensure_metadata_node(label, prefix, name):
    """Đảm bảo node metadata tồn tại, nếu chưa có thì tạo mới kèm ID tự sinh theo chuẩn prefix"""
    if not name or not name.strip():
        return
    name = name.strip()
    
    # Kiểm tra xem đã có node cùng label và name chưa
    query_check = f"MATCH (n:{label} {{name: $name}}) RETURN n.id AS id"
    res = neo4j_conn.query(query_check, {"name": name})
    if not res:
        from services.metadata_service import get_next_metadata_id
        next_id = get_next_metadata_id(label, prefix)
        query_create = f"CREATE (n:{label} {{id: $id, name: $name}})"
        neo4j_conn.query(query_create, {"id": next_id, "name": name})

# =========================
# CREATE DOCUMENT
# =========================
def create_document_service(data):
    doc_id = data.get("id")
    doc_type = data.get("type")

    if doc_type not in ["Book", "Article", "Thesis"]:
        return None

    label = doc_type

    # 🔥 EMBEDDING
    doc_text = build_document_text(
        title=data.get("title"),
        abstract=data.get("abstract"),
        subjects=data.get("subjects"),
        keywords=data.get("keywords")
    )
    embedding = create_embedding(doc_text)

    query = f"""
    CREATE (d:{label} {{
        id: $id,
        title: $title,
        other_title: $other_title,
        year: $year,
        pages: $pages,
        abstract: $abstract,
        file_url: $file_url,
        image_url: $image_url,
        embedding: $embedding,
        status: $status,
        created_at: datetime()
    }})
    RETURN d
    """

    params = {
        "id": doc_id,
        "title": data.get("title"),
        "other_title": data.get("other_title"),
        "year": int(data.get("year")) if data.get("year") else None,
        "pages": data.get("pages"),
        "abstract": data.get("abstract"),
        "file_url": data.get("file_url"),
        "image_url": data.get("image_url"),
        "embedding": embedding,
        "status": data.get("status") or "active"
    }

    neo4j_conn.query(query, params)

    # AUTHORS WITH ROLES
    authors = data.get("authors_json", [])
    for auth in authors:
        name = auth.get("name", "").strip()
        role = auth.get("role", "author").strip()
        if name:
            ensure_metadata_node("Author", "A", name)
            neo4j_conn.query("""
            MERGE (a:Author {name: $name})
            WITH a
            MATCH (d {id: $id})
            MERGE (d)-[r:HAS_AUTHOR {role: $role}]->(a)
            """, {"name": name, "id": doc_id, "role": role})

    # INSTITUTIONS WITH ROLES
    institutions = data.get("institutions_json", [])
    for inst in institutions:
        name = inst.get("name", "").strip()
        role = inst.get("role", "other").strip()
        if name:
            # Map role to specific relation or use ASSOCIATED_WITH
            rel_type = "ASSOCIATED_WITH"
            inst_label = "Publisher" if role == "publisher" else "University"
            inst_prefix = "P" if role == "publisher" else "U"

            if role == "publisher": rel_type = "PUBLISHED_BY"
            elif role == "university": rel_type = "OWNED_BY"

            ensure_metadata_node(inst_label, inst_prefix, name)

            query = f"""
            MERGE (i:{inst_label} {{name: $name}})
            WITH i
            MATCH (d {{id: $id}})
            MERGE (d)-[r:{rel_type}]->(i)
            SET r.role = $role
            """
            neo4j_conn.query(query, {"name": name, "id": doc_id, "role": role})

    # SUBJECTS
    for name in data.get("subjects", []):
        if name.strip():
            ensure_metadata_node("Subject", "S", name)
            neo4j_conn.query("""
            MERGE (s:Subject {name: $name})
            WITH s
            MATCH (d {id: $id})
            MERGE (d)-[:HAS_SUBJECT]->(s)
            """, {"name": name.strip(), "id": doc_id})

    # KEYWORDS
    for name in data.get("keywords", []):
        if name.strip():
            ensure_metadata_node("Keyword", "K", name)
            neo4j_conn.query("""
            MERGE (k:Keyword {name: $name})
            WITH k
            MATCH (d {id: $id})
            MERGE (d)-[:HAS_KEYWORD]->(k)
            """, {"name": name.strip(), "id": doc_id})

    # CATEGORIES
    for name in data.get("categories", []):
        if name.strip():
            ensure_metadata_node("Category", "C", name)
            neo4j_conn.query("""
            MERGE (c:Category {name: $name})
            WITH c
            MATCH (d {id: $id})
            MERGE (d)-[:HAS_CATEGORY]->(c)
            """, {"name": name.strip(), "id": doc_id})

    # LANGUAGES
    for name in data.get("languages", []):
        if name.strip():
            ensure_metadata_node("Language", "L", name)
            neo4j_conn.query("""
            MERGE (l:Language {name: $name})
            WITH l
            MATCH (d {id: $id})
            MERGE (d)-[:IN_LANGUAGE]->(l)
            """, {"name": name.strip(), "id": doc_id})

    # JOURNAL (For Article)
    journal = data.get("journal", "").strip()
    if journal:
        ensure_metadata_node("Journal", "J", journal)
        neo4j_conn.query("""
        MERGE (j:Journal {name: $name})
        WITH j
        MATCH (d {id: $id})
        MERGE (d)-[:PUBLISHED_IN]->(j)
        """, {"name": journal, "id": doc_id})

    # RELATED DOCUMENTS (RELATED_TO)
    related_docs = data.get("related_docs", [])
    for rel_id in related_docs:
        if rel_id.strip():
            neo4j_conn.query("""
            MATCH (d {id: $id}), (r {id: $rel_id})
            WHERE (r:Book OR r:Article OR r:Thesis)
            MERGE (d)-[:RELATED_TO]->(r)
            """, {"id": doc_id, "rel_id": rel_id.strip()})

    reset_faiss_index()
    return doc_id



# =========================
# UPDATE DOCUMENT
# =========================
def update_document_service(doc_id, data):

    # 🔥 RE-EMBEDDING
    doc_text = build_document_text(
        title=data.get("title"),
        abstract=data.get("abstract"),
        subjects=data.get("subjects"),
        keywords=data.get("keywords")
    )
    embedding = create_embedding(doc_text)

    set_clauses = [
        "d.title = $title",
        "d.other_title = $other_title",
        "d.year = $year",
        "d.pages = $pages",
        "d.abstract = $abstract",
        "d.embedding = $embedding",
        "d.status = $status",
        "d.updated_at = datetime()"
    ]
    
    params = {
        "id": doc_id,
        "title": data.get("title"),
        "other_title": data.get("other_title"),
        "year": int(data.get("year")) if data.get("year") else None,
        "pages": data.get("pages"),
        "abstract": data.get("abstract"),
        "embedding": embedding,
        "status": data.get("status") or "active"
    }

    if data.get("image_url"):
        set_clauses.append("d.image_url = $image_url")
        params["image_url"] = data.get("image_url")
    
    if data.get("file_url"):
        set_clauses.append("d.file_url = $file_url")
        params["file_url"] = data.get("file_url")

    query = f"""
    MATCH (d {{id: $id}})
    REMOVE d:Book:Article:Thesis
    WITH d
    SET d:{data.get('type')}
    SET {", ".join(set_clauses)}
    RETURN d
    """

    neo4j_conn.query(query, params)


    # RESET RELATIONS
    neo4j_conn.query("""
    MATCH (d {id: $id})-[r:HAS_AUTHOR|HAS_SUBJECT|HAS_KEYWORD|HAS_CATEGORY|IN_LANGUAGE|PUBLISHED_BY|OWNED_BY|PUBLISHED_IN|RELATED_TO]->()
    DELETE r
    """, {"id": doc_id})

    # RE-ADD ALL (Same logic as create)
    # AUTHORS
    authors = data.get("authors_json", [])
    for auth in authors:
        name = auth.get("name", "").strip()
        role = auth.get("role", "author").strip()
        if name:
            ensure_metadata_node("Author", "A", name)
            neo4j_conn.query("""
            MERGE (a:Author {name: $name})
            WITH a
            MATCH (d {id: $id})
            MERGE (d)-[r:HAS_AUTHOR {role: $role}]->(a)
            """, {"name": name, "id": doc_id, "role": role})

    # INSTITUTIONS
    institutions = data.get("institutions_json", [])
    for inst in institutions:
        name = inst.get("name", "").strip()
        role = inst.get("role", "other").strip()
        if name:
            rel_type = "ASSOCIATED_WITH"
            inst_label = "Publisher" if role == "publisher" else "University"
            inst_prefix = "P" if role == "publisher" else "U"

            if role == "publisher": rel_type = "PUBLISHED_BY"
            elif role == "university": rel_type = "OWNED_BY"

            ensure_metadata_node(inst_label, inst_prefix, name)

            query = f"""
            MERGE (i:{inst_label} {{name: $name}})
            WITH i
            MATCH (d {{id: $id}})
            MERGE (d)-[r:{rel_type}]->(i)
            SET r.role = $role
            """
            neo4j_conn.query(query, {"name": name, "id": doc_id, "role": role})

    # SUBJECTS
    for name in data.get("subjects", []):
        if name.strip():
            ensure_metadata_node("Subject", "S", name)
            neo4j_conn.query("""
            MERGE (s:Subject {name: $name})
            WITH s
            MATCH (d {id: $id})
            MERGE (d)-[:HAS_SUBJECT]->(s)
            """, {"name": name.strip(), "id": doc_id})

    # KEYWORDS
    for name in data.get("keywords", []):
        if name.strip():
            ensure_metadata_node("Keyword", "K", name)
            neo4j_conn.query("""
            MERGE (k:Keyword {name: $name})
            WITH k
            MATCH (d {id: $id})
            MERGE (d)-[:HAS_KEYWORD]->(k)
            """, {"name": name.strip(), "id": doc_id})

    # CATEGORIES
    for name in data.get("categories", []):
        if name.strip():
            ensure_metadata_node("Category", "C", name)
            neo4j_conn.query("""
            MERGE (c:Category {name: $name})
            WITH c
            MATCH (d {id: $id})
            MERGE (d)-[:HAS_CATEGORY]->(c)
            """, {"name": name.strip(), "id": doc_id})

    # LANGUAGES
    for name in data.get("languages", []):
        if name.strip():
            ensure_metadata_node("Language", "L", name)
            neo4j_conn.query("""
            MERGE (l:Language {name: $name})
            WITH l
            MATCH (d {id: $id})
            MERGE (d)-[:IN_LANGUAGE]->(l)
            """, {"name": name.strip(), "id": doc_id})

    # JOURNAL (For Article)
    journal = data.get("journal", "").strip()
    if journal:
        ensure_metadata_node("Journal", "J", journal)
        neo4j_conn.query("""
        MERGE (j:Journal {name: $name})
        WITH j
        MATCH (d {id: $id})
        MERGE (d)-[:PUBLISHED_IN]->(j)
        """, {"name": journal, "id": doc_id})

    # RE-ADD RELATED DOCUMENTS (RELATED_TO)
    related_docs = data.get("related_docs", [])
    for rel_id in related_docs:
        if rel_id.strip():
            neo4j_conn.query("""
            MATCH (d {id: $id}), (r {id: $rel_id})
            WHERE (r:Book OR r:Article OR r:Thesis)
            MERGE (d)-[:RELATED_TO]->(r)
            """, {"id": doc_id, "rel_id": rel_id.strip()})

    reset_faiss_index()
    return True



# =========================
# DELETE DOCUMENT
# =========================
def delete_document_service(doc_id):
    query = """
    MATCH (d {id: $id})
    DETACH DELETE d
    """
    result = neo4j_conn.query(query, {"id": doc_id})
    reset_faiss_index()
    return result
