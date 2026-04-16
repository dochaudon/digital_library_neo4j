from database.neo4j_connection import neo4j_conn


# =========================
# COMMON TYPE RESOLVER
# =========================
TYPE_CASE = """
CASE
    WHEN d:Book THEN "Book"
    WHEN d:Article THEN "Article"
    WHEN d:Thesis THEN "Thesis"
    ELSE coalesce(d.type, "Document")
END
"""

TYPE_CASE_RELATED = """
CASE
    WHEN related:Book THEN "Book"
    WHEN related:Article THEN "Article"
    WHEN related:Thesis THEN "Thesis"
    ELSE coalesce(related.type, "Document")
END
"""


# =========================
# GET DOCUMENT BY ID
# =========================
def get_document_by_id(doc_id):
    query = f"""
    MATCH (d)
    WHERE d.id = $id AND (d:Book OR d:Article OR d:Thesis)

    OPTIONAL MATCH (d)-[r:HAS_AUTHOR]->(a:Author)
    OPTIONAL MATCH (d)-[:HAS_SUBJECT]->(s:Subject)
    OPTIONAL MATCH (d)-[:HAS_KEYWORD]->(k:Keyword)
    OPTIONAL MATCH (d)-[:PUBLISHED_BY]->(p:Institution)
    OPTIONAL MATCH (d)-[:SUBMITTED_TO]->(u:Institution)

    RETURN
        d.id AS id,
        d.title AS title,
        d.year AS year,
        d.pages AS pages,
        d.abstract AS abstract,
        d.file_url AS file_url,

        {TYPE_CASE} AS type,

        collect(DISTINCT {{
            name: a.name,
            role: coalesce(r.role, "author")
        }}) AS authors_info,

        collect(DISTINCT s.name) AS subjects,
        collect(DISTINCT k.name) AS keywords,

        head(collect(DISTINCT p.name)) AS publisher,
        head(collect(DISTINCT u.name)) AS university
    """

    result = neo4j_conn.query(query, {"id": doc_id})
    return result[0] if result else None
# =========================
# GET ALL DOCUMENTS
# =========================
def get_all_documents(skip=0, limit=20):
    query = f"""
    MATCH (d)
    WHERE d:Book OR d:Article OR d:Thesis

    RETURN
        d.id AS id,
        d.title AS title,
        d.year AS year,
        {TYPE_CASE} AS type

    ORDER BY d.year DESC
    SKIP $skip LIMIT $limit
    """

    return neo4j_conn.query(query, {
        "skip": skip,
        "limit": limit
    })


# =========================
# COUNT DOCUMENTS
# =========================
def count_documents():
    query = """
    MATCH (d)
    WHERE d:Book OR d:Article OR d:Thesis
    RETURN count(d) AS total
    """

    result = neo4j_conn.query(query)
    return result[0]["total"] if result else 0


# =========================
# GET DOCUMENTS BY TYPE
# =========================
def get_documents_by_type(doc_type, skip=0, limit=20):
    query = f"""
    MATCH (d)
    WHERE
        ($type = "Book" AND d:Book) OR
        ($type = "Article" AND d:Article) OR
        ($type = "Thesis" AND d:Thesis)

    RETURN
        d.id AS id,
        d.title AS title,
        d.year AS year,
        {TYPE_CASE} AS type

    ORDER BY d.year DESC
    SKIP $skip LIMIT $limit
    """

    return neo4j_conn.query(query, {
        "type": doc_type,
        "skip": skip,
        "limit": limit
    })


# =========================
# GET RELATED DOCUMENTS
# =========================
def get_related_documents(doc_id, limit=10):
    query = f"""
    MATCH (d {{id: $id}})-[:RELATED_TO]->(related)

    WHERE related:Book OR related:Article OR related:Thesis

    RETURN
        related.id AS id,
        related.title AS title,
        related.year AS year,
        {TYPE_CASE_RELATED} AS type

    LIMIT $limit
    """

    return neo4j_conn.query(query, {
        "id": doc_id,
        "limit": limit
    })

