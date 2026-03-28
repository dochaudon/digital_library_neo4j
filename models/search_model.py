from database.neo4j_connection import neo4j_conn

FULLTEXT_INDEX = "documentSearchIndex"


# =========================
# FULLTEXT SEARCH
# =========================
def search_documents_by_title(query, limit=20):

    if not query:
        return []

    cypher = """
    CALL db.index.fulltext.queryNodes($index, $query) YIELD node, score
    WHERE node:Book OR node:Article OR node:Thesis

    RETURN
        node.id AS id,
        node.title AS title,
        node.year AS year,
        labels(node)[0] AS type,
        score AS relevance_score,
        'keyword' AS source

    ORDER BY score DESC
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
# GRAPH SEARCH (FIXED)
# =========================
def search_documents_by_graph(filters, limit=20):

    if not any(filters.values()):
        return []

    cypher = """
    MATCH (d)
    WHERE d:Book OR d:Article OR d:Thesis

    OPTIONAL MATCH (d)-[:WRITTEN_BY]->(a:Author)
    OPTIONAL MATCH (d)-[:BELONGS_TO]->(t:Topic)
    OPTIONAL MATCH (d)-[:PUBLISHED_BY]->(p:Publisher)
    OPTIONAL MATCH (d)-[:SUBMITTED_TO]->(u:University)

    WITH d,
         collect(DISTINCT a.name) AS authors,
         collect(DISTINCT t.name) AS topics,
         head(collect(DISTINCT p.name)) AS publisher,
         head(collect(DISTINCT u.name)) AS university

    WHERE
        ($doc_type IS NULL OR labels(d)[0] = $doc_type)

        AND ($author IS NULL OR
            ANY(x IN authors WHERE toLower(x) = toLower($author)))

        AND ($topic IS NULL OR
            ANY(x IN topics WHERE toLower(x) CONTAINS toLower($topic)))

        AND ($publisher IS NULL OR
            (publisher IS NOT NULL AND toLower(publisher) CONTAINS toLower($publisher)))

        AND ($university IS NULL OR
            (university IS NOT NULL AND toLower(university) CONTAINS toLower($university)))

        AND ($year IS NULL OR d.year = $year)

        AND ($author IS NULL OR size(authors) > 0)

    WITH d, authors, topics, publisher, university,

    (
        CASE WHEN $doc_type IS NOT NULL AND labels(d)[0]=$doc_type THEN 1 ELSE 0 END +

        CASE 
            WHEN $author IS NOT NULL AND 
            ANY(x IN authors WHERE toLower(x) = toLower($author)) 
            THEN 3 ELSE 0 END +

        CASE 
            WHEN $topic IS NOT NULL AND 
            ANY(x IN topics WHERE toLower(x) CONTAINS toLower($topic)) 
            THEN 2 ELSE 0 END +

        CASE 
            WHEN $publisher IS NOT NULL AND 
            publisher IS NOT NULL AND 
            toLower(publisher) CONTAINS toLower($publisher) 
            THEN 1 ELSE 0 END +

        CASE 
            WHEN $university IS NOT NULL AND 
            university IS NOT NULL AND 
            toLower(university) CONTAINS toLower($university) 
            THEN 1 ELSE 0 END +

        CASE 
            WHEN $year IS NOT NULL AND d.year = $year 
            THEN 1 ELSE 0 END
    ) AS score

    RETURN
        d.id AS id,
        d.title AS title,
        d.year AS year,
        labels(d)[0] AS type,
        authors,
        topics,
        publisher,
        university,
        score AS relevance_score,
        'graph' AS source

    ORDER BY score DESC, d.year DESC
    LIMIT $limit
    """

    return neo4j_conn.query(
        cypher,
        {
            "doc_type": filters.get("doc_type"),
            "author": filters.get("author"),
            "topic": filters.get("topic"),
            "publisher": filters.get("publisher"),
            "university": filters.get("university"),
            "year": filters.get("year"),
            "limit": limit
        }
    )


# =========================
# LATEST DOCUMENTS
# =========================
def get_latest_documents(limit=20):
    query = """
    MATCH (d)
    WHERE d:Book OR d:Article OR d:Thesis
    RETURN d.id AS id, d.title AS title, d.year AS year, labels(d)[0] AS type
    ORDER BY d.year DESC
    LIMIT $limit
    """
    return neo4j_conn.query(query, {"limit": limit})