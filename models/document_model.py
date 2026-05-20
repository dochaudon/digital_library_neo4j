from database.neo4j_connection import neo4j_conn

# Consts for Type Mapping
TYPE_CASE_RELATED = """
    CASE 
        WHEN "Book" IN labels(related) THEN "Book"
        WHEN "Article" IN labels(related) THEN "Article"
        WHEN "Thesis" IN labels(related) THEN "Thesis"
        ELSE "Other"
    END
"""

# =========================
# GET ALL (PAGINATION)
# =========================
def get_all_documents(skip=0, limit=20, q=None):
    query = f"""
    MATCH (d)
    WHERE (d:Book OR d:Article OR d:Thesis)
      AND ($q IS NULL OR d.title CONTAINS $q)
    OPTIONAL MATCH (d)-[:HAS_AUTHOR]->(a:Author)
    OPTIONAL MATCH (d)-[:HAS_SUBJECT]->(s:Subject)
    RETURN 
        d.id AS id, 
        d.title AS title, 
        d.year AS year, 
        d.image_url AS image_url,
        CASE 
            WHEN "Book" IN labels(d) THEN "Book"
            WHEN "Article" IN labels(d) THEN "Article"
            WHEN "Thesis" IN labels(d) THEN "Thesis"
            ELSE "Other"
        END AS type,
        collect(DISTINCT a.name) AS authors,
        collect(DISTINCT s.name) AS subjects
    ORDER BY toInteger(substring(d.id, 1)) DESC, d.year DESC
    SKIP $skip LIMIT $limit
    """
    return neo4j_conn.query(query, {"skip": skip, "limit": limit, "q": q})


# =========================
# GET BY ID
# =========================
def get_document_by_id(doc_id):
    query = """
    MATCH (d {id: $id})
    OPTIONAL MATCH (d)-[ra:HAS_AUTHOR]->(a:Author)
    OPTIONAL MATCH (d)-[:HAS_SUBJECT]->(s:Subject)
    OPTIONAL MATCH (d)-[:HAS_KEYWORD]->(k:Keyword)
    OPTIONAL MATCH (d)-[:HAS_CATEGORY]->(c:Category)
    OPTIONAL MATCH (d)-[:IN_LANGUAGE]->(l:Language)
    OPTIONAL MATCH (d)-[:PUBLISHED_BY]->(p:Publisher)
    OPTIONAL MATCH (d)-[:OWNED_BY]->(u:University)
    OPTIONAL MATCH (d)-[:PUBLISHED_IN]->(j:Journal)
    OPTIONAL MATCH (d)-[:RELATED_TO]->(rd)

    RETURN 
        d,
        labels(d) AS doc_labels,
        collect(DISTINCT {name: a.name, role: ra.role}) AS authors,
        collect(DISTINCT s.name) AS subjects,
        collect(DISTINCT k.name) AS keywords,
        collect(DISTINCT c.name) AS categories,
        collect(DISTINCT l.name) AS languages,
        collect(DISTINCT p.name) AS publishers,
        collect(DISTINCT u.name) AS universities,
        j.name AS journal,
        collect(DISTINCT rd.id) AS related_docs
    """
    result = neo4j_conn.query(query, {"id": doc_id})
    if not result:
        return None

    row = result[0]
    doc = dict(row["d"])
    
    # Mapping labels to type
    labels = row["doc_labels"]
    if "Book" in labels: doc["type"] = "Book"
    elif "Article" in labels: doc["type"] = "Article"
    elif "Thesis" in labels: doc["type"] = "Thesis"
    else: doc["type"] = "Other"

    # Grouping authors by role
    groups = {}
    for auth in row["authors"]:
        role = auth["role"] or "author"
        if role not in groups: groups[role] = []
        groups[role].append(auth)

    doc["author_groups"] = groups
    doc["subjects"] = row["subjects"]
    doc["keywords"] = row["keywords"]
    doc["categories"] = row["categories"]
    doc["languages"] = row["languages"]
    doc["publishers"] = row["publishers"]
    doc["universities"] = row["universities"]
    doc["journal"] = row["journal"]
    doc["related_docs"] = row["related_docs"]
    doc["authors_info"] = row["authors"]

    return doc


# =========================
# GET BY TYPE
# =========================
def get_documents_by_type(doc_types, skip=0, limit=20):
    query = f"""
    MATCH (d)
    WHERE ANY(label IN labels(d) WHERE label IN $types)
    OPTIONAL MATCH (d)-[:HAS_AUTHOR]->(a:Author)
    OPTIONAL MATCH (d)-[:HAS_SUBJECT]->(s:Subject)
    RETURN 
        d.id AS id, 
        d.title AS title, 
        d.year AS year, 
        d.image_url AS image_url,
        CASE 
            WHEN "Book" IN labels(d) THEN "Book"
            WHEN "Article" IN labels(d) THEN "Article"
            WHEN "Thesis" IN labels(d) THEN "Thesis"
            ELSE "Other"
        END AS type,
        collect(DISTINCT a.name) AS authors,
        collect(DISTINCT s.name) AS subjects
    ORDER BY toInteger(substring(d.id, 1)) DESC, d.year DESC
    SKIP $skip LIMIT $limit
    """
    return neo4j_conn.query(query, {"types": doc_types, "skip": skip, "limit": limit})


# =========================
# COUNT
# =========================
def count_documents(q=None):
    query = """
    MATCH (d)
    WHERE (d:Book OR d:Article OR d:Thesis)
      AND ($q IS NULL OR d.title CONTAINS $q)
    RETURN count(d) AS total
    """
    result = neo4j_conn.query(query, {"q": q})
    return result[0]["total"] if result else 0


# =========================
# RELATED DOCUMENTS (GENERAL)
# =========================
def get_related_documents(doc_id, limit=5):
    query = f"""
    MATCH (d {{id: $id}})-[:HAS_SUBJECT|HAS_KEYWORD]->(tag)<-[:HAS_SUBJECT|HAS_KEYWORD]-(related)
    WHERE related <> d
    RETURN DISTINCT
        related.id AS id, 
        related.title AS title, 
        related.year AS year, 
        related.image_url AS id_url,
        {TYPE_CASE_RELATED} AS type,
        count(tag) AS score
    ORDER BY score DESC, related.year DESC
    LIMIT $limit
    """
    return neo4j_conn.query(query, {"id": doc_id, "limit": limit})


# =========================
# RELATED BY AUTHOR (NEW)
# =========================
def get_related_documents_by_author(doc_id, limit=10):
    query = f"""
    MATCH (d {{id: $id}})-[:HAS_AUTHOR]->(a:Author)<-[:HAS_AUTHOR]-(related)
    WHERE related <> d
      AND (related:Book OR related:Article OR related:Thesis)

    RETURN DISTINCT
        related.id AS id,
        related.title AS title,
        related.year AS year,
        related.image_url AS image_url,
        {TYPE_CASE_RELATED} AS type

    ORDER BY related.year DESC
    LIMIT $limit
    """
    return neo4j_conn.query(query, {"id": doc_id, "limit": limit})