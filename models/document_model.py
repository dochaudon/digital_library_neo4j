from database.neo4j_connection import neo4j_conn


# =========================
# TYPE RESOLVER
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
# 🔥 GROUP AUTHOR ROLE (CORE)
# =========================
def group_authors(author_roles):
    grouped = {
        "author": [],
        "contributor": [],
        "supervisor": [],
        "editor": []
    }

    for item in author_roles:
        if not item or not item.get("name"):
            continue

        role = item.get("role") or "author"

        if role not in grouped:
            grouped[role] = []

        grouped[role].append({
            "name": item["name"],
            "institution": item.get("institution")
        })

    return grouped


# =========================
# 🔥 GET DOCUMENT DETAIL (FINAL)
# =========================
def get_document_by_id(doc_id):

    query = f"""
    MATCH (d)
    WHERE d.id = $id AND (d:Book OR d:Article OR d:Thesis)

    RETURN
        d.id AS id,
        d.title AS title,
        d.other_title AS other_title,
        d.year AS year,
        d.pages AS pages,
        d.abstract AS abstract,
        d.file_url AS file_url,
        d.image_url AS image_url,
        {TYPE_CASE} AS type,

        [(d)-[r:HAS_AUTHOR]->(a:Author) | {{
            name: a.name,
            role: coalesce(r.role, "author")
        }}] AS authors_info,

        [(d)-[:HAS_SUBJECT]->(s:Subject) | s.name] AS subjects,
        [(d)-[:HAS_KEYWORD]->(k:Keyword) | k.name] AS keywords,
        [(d)-[:IN_CATEGORY]->(c:Category) | c.name] AS categories,
        [(d)-[:IN_LANGUAGE]->(l:Language) | l.name] AS languages,
        [(d)-[:PUBLISHED_BY]->(p) | p.name] AS publishers,
        [(d)-[:OWNED_BY]->(u) | u.name] AS universities,
        [(d)-[:PUBLISHED_IN]->(j:Journal) | j.name][0] AS journal
    """


    result = neo4j_conn.query(query, {"id": doc_id})

    if not result:
        return None

    doc = result[0]

    # 🔥 GROUP ROLE
    doc["author_groups"] = group_authors(doc.get("authors_info", []))

    return doc



# =========================
# GET ALL DOCUMENTS
# =========================
def get_all_documents(skip=0, limit=20, q=None):
    where_clause = "WHERE (d:Book OR d:Article OR d:Thesis)"
    params = {"skip": skip, "limit": limit}
    
    if q:
        where_clause += " AND toLower(d.title) CONTAINS toLower($q)"
        params["q"] = q

    query = f"""
    MATCH (d)
    {where_clause}

    OPTIONAL MATCH (d)-[:HAS_AUTHOR]->(a:Author)

    RETURN
        d.id AS id,
        d.title AS title,
        d.year AS year,
        d.image_url AS image_url,
        {TYPE_CASE} AS type,
        collect(DISTINCT a.name) AS authors

    ORDER BY d.year DESC
    SKIP $skip LIMIT $limit
    """

    return neo4j_conn.query(query, params)


# =========================
# COUNT
# =========================
def count_documents(q=None):
    where_clause = "WHERE (d:Book OR d:Article OR d:Thesis)"
    params = {}
    
    if q:
        where_clause += " AND toLower(d.title) CONTAINS toLower($q)"
        params["q"] = q

    query = f"""
    MATCH (d)
    {where_clause}
    RETURN count(d) AS total
    """

    result = neo4j_conn.query(query, params)
    return result[0]["total"] if result else 0


# =========================
# BY TYPE
# =========================
def get_documents_by_type(doc_type, skip=0, limit=20):
    query = f"""
    MATCH (d)
    WHERE $type IS NULL OR ANY(label IN labels(d) WHERE label IN $type)

    OPTIONAL MATCH (d)-[:HAS_AUTHOR]->(a:Author)

    RETURN
        d.id AS id,
        d.title AS title,
        d.year AS year,
        d.image_url AS image_url,
        {TYPE_CASE} AS type,
        collect(DISTINCT a.name) AS authors

    ORDER BY d.year DESC
    SKIP $skip LIMIT $limit
    """

    return neo4j_conn.query(query, {
        "type": doc_type,
        "skip": skip,
        "limit": limit
    })


# =========================
# RELATED
# =========================
def get_related_documents(doc_id, limit=5):
    query = f"""
    MATCH (d {{id: $id}})-[:HAS_SUBJECT]->(s)<-[:HAS_SUBJECT]-(related)
    WHERE related <> d
      AND (related:Book OR related:Article OR related:Thesis)

    RETURN
        related.id AS id,
        related.title AS title,
        related.year AS year,
        related.image_url AS image_url,
        {TYPE_CASE_RELATED} AS type

    ORDER BY related.year DESC
    LIMIT $limit
    """

    return neo4j_conn.query(query, {
        "id": doc_id,
        "limit": limit
    })