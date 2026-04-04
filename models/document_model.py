from database.neo4j_connection import neo4j_conn


# =========================
# GET DOCUMENT BY ID
# =========================
def get_document_by_id(doc_id):
    query = """
    MATCH (d)
    WHERE d.id = $id AND (d:Book OR d:Article OR d:Thesis)

    OPTIONAL MATCH (d)-[:HAS_AUTHOR]->(a:Author)
    OPTIONAL MATCH (d)-[:HAS_SUBJECT]->(s:Subject)
    OPTIONAL MATCH (d)-[:HAS_KEYWORD]->(k:Keyword)
    OPTIONAL MATCH (d)-[:PUBLISHED_BY]->(p:Institution)
    OPTIONAL MATCH (d)-[:SUBMITTED_TO]->(u:Institution)

    RETURN
        d.id AS id,
        d.title AS title,
        d.year AS year,
        labels(d)[0] AS type,

        collect(DISTINCT a.name) AS authors,
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
    query = """
    MATCH (d)
    WHERE d:Book OR d:Article OR d:Thesis

    RETURN
        d.id AS id,
        d.title AS title,
        d.year AS year,
        labels(d)[0] AS type

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
    query = """
    MATCH (d)
    WHERE labels(d)[0] = $type

    RETURN
        d.id AS id,
        d.title AS title,
        d.year AS year,
        labels(d)[0] AS type

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
    query = """
    MATCH (d {id: $id})-[:RELATED_TO]->(related)

    WHERE related:Book OR related:Article OR related:Thesis

    RETURN
        related.id AS id,
        related.title AS title,
        related.year AS year,
        labels(related)[0] AS type

    LIMIT $limit
    """

    return neo4j_conn.query(query, {
        "id": doc_id,
        "limit": limit
    })