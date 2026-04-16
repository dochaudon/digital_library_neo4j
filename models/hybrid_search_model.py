from database.neo4j_connection import neo4j_conn

FULLTEXT_INDEX = "documentSearchIndex"


# =========================
# TYPE RESOLVER
# =========================
TYPE_CASE_NODE = """
CASE
    WHEN node:Book THEN "Book"
    WHEN node:Article THEN "Article"
    WHEN node:Thesis THEN "Thesis"
    ELSE coalesce(node.type, "Document")
END
"""

TYPE_CASE_D = """
CASE
    WHEN d:Book THEN "Book"
    WHEN d:Article THEN "Article"
    WHEN d:Thesis THEN "Thesis"
    ELSE coalesce(d.type, "Document")
END
"""


# =========================
# FULLTEXT SEARCH (🔥 FIX)
# =========================
def search_documents_fulltext(query, limit=20):

    if not query:
        return []

    cypher = f"""
    CALL db.index.fulltext.queryNodes($index, $query)
    YIELD node, score

    WHERE node:Book OR node:Article OR node:Thesis

    OPTIONAL MATCH (node)-[:HAS_AUTHOR]->(a:Author)

    WITH node,
         score,
         collect(DISTINCT CASE 
            WHEN a.name IS NOT NULL THEN a.name 
         END) AS authors

    RETURN
        node.id AS id,
        node.title AS title,
        coalesce(node.year, 0) AS year,
        {TYPE_CASE_NODE} AS type,
        authors,
        score * 2 AS relevance_score,
        'keyword' AS source

    ORDER BY relevance_score DESC
    LIMIT $limit
    """

    return neo4j_conn.query(
        cypher,
        {
            "index": FULLTEXT_INDEX,
            "query": query,
            "limit": limit
        }
    )


# =========================
# GRAPH SEARCH
# =========================
def search_documents_graph(filters, limit=20):

    if not any(filters.values()):
        return []

    cypher = f"""
    MATCH (d)
    WHERE d:Book OR d:Article OR d:Thesis

    OPTIONAL MATCH (d)-[:HAS_AUTHOR]->(a:Author)
    OPTIONAL MATCH (d)-[:HAS_SUBJECT]->(s:Subject)
    OPTIONAL MATCH (d)-[:PUBLISHED_BY]->(p:Institution)
    OPTIONAL MATCH (d)-[:SUBMITTED_TO]->(u:Institution)

    WITH d,
         collect(DISTINCT CASE 
            WHEN a.name IS NOT NULL THEN a.name 
         END) AS authors,
         collect(DISTINCT s.name) AS subjects,
         head(collect(DISTINCT p.name)) AS publisher,
         head(collect(DISTINCT u.name)) AS university

    WHERE
        ($doc_type IS NULL OR
            ($doc_type = "Book" AND d:Book) OR
            ($doc_type = "Article" AND d:Article) OR
            ($doc_type = "Thesis" AND d:Thesis)
        )

        AND ($author IS NULL OR
            ANY(x IN authors WHERE toLower(x) CONTAINS toLower($author)))

        AND ($subject IS NULL OR
            ANY(x IN subjects WHERE toLower(x) CONTAINS toLower($subject)))

        AND ($publisher IS NULL OR
            (publisher IS NOT NULL AND toLower(publisher) CONTAINS toLower($publisher)))

        AND ($university IS NULL OR
            (university IS NOT NULL AND toLower(university) CONTAINS toLower($university)))

        AND ($year IS NULL OR d.year = $year)

    RETURN
        d.id AS id,
        d.title AS title,
        coalesce(d.year, 0) AS year,
        {TYPE_CASE_D} AS type,
        authors,
        subjects,
        publisher,
        university,
        2 AS relevance_score,
        'graph' AS source

    LIMIT $limit
    """

    return neo4j_conn.query(cypher, {
        "doc_type": filters.get("doc_type"),
        "author": filters.get("author"),
        "subject": filters.get("subject"),
        "publisher": filters.get("publisher"),
        "university": filters.get("university"),
        "year": filters.get("year"),
        "limit": limit
    })


# =========================
# HYBRID SEARCH (FINAL)
# =========================
def hybrid_search(query, filters=None, limit=20):

    filters = filters or {}

    if any(filters.values()):
            return search_documents_graph(filters, limit)

        # 🔥 nếu không có filter → dùng fulltext
    return search_documents_fulltext(query, limit)


# =========================
# LATEST DOCUMENTS
# =========================
def get_latest_documents(limit=20):
    query = f"""
    MATCH (d)
    WHERE d:Book OR d:Article OR d:Thesis

    OPTIONAL MATCH (d)-[:HAS_AUTHOR]->(a:Author)
    OPTIONAL MATCH (d)-[:PUBLISHED_BY]->(p:Institution)
    OPTIONAL MATCH (d)-[:SUBMITTED_TO]->(u:Institution)

    WITH d,
         collect(DISTINCT CASE 
            WHEN a.name IS NOT NULL THEN a.name 
         END) AS authors,
         head(collect(DISTINCT p.name)) AS publisher,
         head(collect(DISTINCT u.name)) AS university

    RETURN
        d.id AS id,
        d.title AS title,
        coalesce(d.year, 0) AS year,
        {TYPE_CASE_D} AS type,
        authors,
        publisher,
        university

    ORDER BY d.year DESC
    LIMIT $limit
    """

    return neo4j_conn.query(query, {"limit": limit})