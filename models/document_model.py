from database.neo4j_connection import neo4j_conn

# Consts for Type Mapping
TYPE_CASE_RELATED = """
    CASE 
        WHEN related.type = 'book' THEN 'Book'
        WHEN related.type = 'article' THEN 'Article'
        WHEN related.type = 'thesis' THEN 'Thesis'
        ELSE 'Other'
    END
"""

# =========================
# GET ALL (PAGINATION)
# =========================
def get_all_documents(skip=0, limit=20, q=None, include_hidden=False):
    query = f"""
    MATCH (d:Document)
    WHERE ($q IS NULL OR d.title CONTAINS $q)
      AND ($include_hidden OR d.status IS NULL OR d.status = 'active')
    OPTIONAL MATCH (d)-[:HAS_AUTHOR]->(a:Author)
    OPTIONAL MATCH (d)-[:HAS_SUBJECT]->(s:Subject)
    RETURN 
        d.id AS id, 
        d.title AS title, 
        d.year AS year, 
        d.image_url AS image_url,
        d.status AS status,
        CASE 
            WHEN d.type = 'book' THEN 'Book'
            WHEN d.type = 'article' THEN 'Article'
            WHEN d.type = 'thesis' THEN 'Thesis'
            ELSE 'Other'
        END AS type,
        collect(DISTINCT a.name) AS authors,
        collect(DISTINCT s.name) AS subjects
    ORDER BY toInteger(substring(d.id, 1)) DESC, d.year DESC
    SKIP $skip LIMIT $limit
    """
    return neo4j_conn.query(query, {"skip": skip, "limit": limit, "q": q, "include_hidden": include_hidden})


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
        d.type AS doc_type,
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
    doc_type = row.get("doc_type")
    if doc_type == "book": doc["type"] = "Book"
    elif doc_type == "article": doc["type"] = "Article"
    elif doc_type == "thesis": doc["type"] = "Thesis"
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
def get_documents_by_type(doc_types, skip=0, limit=20, include_hidden=False):
    doc_types = [t.lower() for t in doc_types]
    query = f"""
    MATCH (d:Document)
    WHERE d.type IN $types
      AND ($include_hidden OR d.status IS NULL OR d.status = 'active')
    OPTIONAL MATCH (d)-[:HAS_AUTHOR]->(a:Author)
    OPTIONAL MATCH (d)-[:HAS_SUBJECT]->(s:Subject)
    RETURN 
        d.id AS id, 
        d.title AS title, 
        d.year AS year, 
        d.image_url AS image_url,
        d.status AS status,
        CASE 
            WHEN d.type = 'book' THEN 'Book'
            WHEN d.type = 'article' THEN 'Article'
            WHEN d.type = 'thesis' THEN 'Thesis'
            ELSE 'Other'
        END AS type,
        collect(DISTINCT a.name) AS authors,
        collect(DISTINCT s.name) AS subjects
    ORDER BY toInteger(substring(d.id, 1)) DESC, d.year DESC
    SKIP $skip LIMIT $limit
    """
    return neo4j_conn.query(query, {"types": doc_types, "skip": skip, "limit": limit, "include_hidden": include_hidden})


# =========================
# COUNT
# =========================
def count_documents(q=None, include_hidden=False):
    query = """
    MATCH (d:Document)
    WHERE ($q IS NULL OR d.title CONTAINS $q)
      AND ($include_hidden OR d.status IS NULL OR d.status = 'active')
    RETURN count(d) AS total
    """
    result = neo4j_conn.query(query, {"q": q, "include_hidden": include_hidden})
    return result[0]["total"] if result else 0


# =========================
# RELATED DOCUMENTS (GENERAL)
# =========================
def get_related_documents(doc_id, limit=5):
    query = f"""
    MATCH (d:Document {{id: $id}})
    MATCH (related:Document)
    WHERE related <> d
    
    // 1. Direct document relation score (weight 15)
    WITH d, related
    OPTIONAL MATCH (d)-[:RELATED_TO]-(related)
    WITH d, related, 
         CASE WHEN (d)-[:RELATED_TO]-(related) THEN 15 ELSE 0 END AS rel_score
         
    // 2. Shared author score (weight 5)
    OPTIONAL MATCH (d)-[:HAS_AUTHOR]->(a:Author)<-[:HAS_AUTHOR]-(related)
    WITH d, related, rel_score, 
         count(distinct a) * 5 AS author_score
         
    // 3. Subject relation path score (0 to 3 hops)
    OPTIONAL MATCH (d)-[:HAS_SUBJECT]->(s1:Subject), (related)-[:HAS_SUBJECT]->(s2:Subject)
    WITH d, related, rel_score, author_score, s1, s2
    OPTIONAL MATCH p = shortestPath((s1)-[:RELATED_TO*0..3]-(s2))
    WITH d, related, rel_score, author_score,
         max(CASE 
             WHEN p IS NULL THEN 0
             WHEN length(p) = 0 THEN 8
             WHEN length(p) = 1 THEN 6
             WHEN length(p) = 2 THEN 4
             WHEN length(p) = 3 THEN 2
             ELSE 0
         END) AS subject_score
         
    // 4. Shared keyword score (weight 3)
    OPTIONAL MATCH (d)-[:HAS_KEYWORD]->(k:Keyword)<-[:HAS_KEYWORD]-(related)
    WITH related, rel_score, author_score, subject_score, 
         count(distinct k) * 3 AS keyword_score
         
    WITH related, (rel_score + author_score + subject_score + keyword_score) AS final_score
    WHERE final_score > 0
    
    RETURN 
        related.id AS id, 
        related.title AS title, 
        related.year AS year, 
        related.image_url AS image_url,
        {TYPE_CASE_RELATED} AS type,
        final_score AS score
    ORDER BY score DESC, related.year DESC
    LIMIT $limit
    """
    return neo4j_conn.query(query, {"id": doc_id, "limit": limit})


# =========================
# RELATED BY AUTHOR (NEW)
# =========================
def get_related_documents_by_author(doc_id, limit=10):
    query = f"""
    MATCH (d:Document {{id: $id}})-[:HAS_AUTHOR]->(a:Author)<-[:HAS_AUTHOR]-(related:Document)
    WHERE related <> d

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