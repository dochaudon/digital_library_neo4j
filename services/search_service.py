from database.neo4j_connection import neo4j_conn

FULLTEXT_INDEX = "documentSearchIndex"


# =========================
# TYPE RESOLVER
# =========================
TYPE_CASE = """
CASE
    WHEN node:Book THEN "Book"
    WHEN node:Article THEN "Article"
    WHEN node:Thesis THEN "Thesis"
    ELSE coalesce(node.type, "Document")
END
"""


# =========================
# FULLTEXT SEARCH
# =========================
def search_fulltext(query, limit=20):

    if not query:
        return []

    cypher = f"""
    CALL db.index.fulltext.queryNodes($index, $query)
    YIELD node, score

    WHERE node:Book OR node:Article OR node:Thesis

    OPTIONAL MATCH (node)-[:HAS_AUTHOR]->(a:Author)

    RETURN
        node.id AS id,
        node.title AS title,
        node.year AS year,
        {TYPE_CASE} AS type,
        collect(DISTINCT a.name) AS authors,
        score AS score,
        'fulltext' AS source

    ORDER BY score DESC
    LIMIT $limit
    """

    return neo4j_conn.query(cypher, {
        "index": FULLTEXT_INDEX,
        "query": query,
        "limit": limit
    })


# =========================
# GRAPH SEARCH (FILTER)
# =========================
def search_graph(filters, limit=20):

    if not any(filters.values()):
        return []

    cypher = """
    MATCH (d)
    WHERE d:Book OR d:Article OR d:Thesis

    OPTIONAL MATCH (d)-[:HAS_AUTHOR]->(a:Author)
    OPTIONAL MATCH (d)-[:HAS_SUBJECT]->(s:Subject)

    WITH d,
         collect(DISTINCT a.name) AS authors,
         collect(DISTINCT s.name) AS subjects

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

        AND ($year IS NULL OR d.year = $year)

    RETURN
        d.id AS id,
        d.title AS title,
        d.year AS year,
        CASE
            WHEN d:Book THEN "Book"
            WHEN d:Article THEN "Article"
            WHEN d:Thesis THEN "Thesis"
        END AS type,
        authors,
        1 AS score,
        'graph' AS source

    ORDER BY d.year DESC
    LIMIT $limit
    """

    return neo4j_conn.query(cypher, {
        "doc_type": filters.get("doc_type"),
        "author": filters.get("author"),
        "subject": filters.get("subject"),
        "year": filters.get("year"),
        "limit": limit
    })


# =========================
# 🔥 HYBRID SEARCH (CORE)
# =========================
def hybrid_search(query="", filters=None, limit=20):

    filters = filters or {}

    results_fulltext = search_fulltext(query, limit)
    results_graph = search_graph(filters, limit)

    # =========================
    # MERGE + REMOVE DUPLICATE
    # =========================
    merged = {}

    for item in results_fulltext:
        merged[item["id"]] = item

    for item in results_graph:
        if item["id"] in merged:
            # boost score nếu có cả graph + fulltext
            merged[item["id"]]["score"] += 1
        else:
            merged[item["id"]] = item

    # =========================
    # SORT
    # =========================
    results = list(merged.values())

    results.sort(key=lambda x: (-x.get("score", 0), - (x.get("year") or 0)))

    return results[:limit]


# =========================
# MAIN SEARCH (PUBLIC)
# =========================
def search_documents(query="", filters=None, limit=20):
    return hybrid_search(query, filters, limit)


# =========================
# LATEST DOCUMENTS
# =========================
def get_latest_documents(limit=20):
    query = """
    MATCH (d)
    WHERE d:Book OR d:Article OR d:Thesis

    OPTIONAL MATCH (d)-[:HAS_AUTHOR]->(a:Author)

    RETURN
        d.id AS id,
        d.title AS title,
        d.year AS year,
        d.image_url AS image_url,  
        CASE
            WHEN d:Book THEN "Book"
            WHEN d:Article THEN "Article"
            WHEN d:Thesis THEN "Thesis"
        END AS type,
        collect(DISTINCT a.name) AS authors

    ORDER BY d.year DESC
    LIMIT $limit
    """

    return neo4j_conn.query(query, {"limit": limit})