from database.neo4j_connection import neo4j_conn

FULLTEXT_INDEX = "documentSearchIndex"


# =========================
# SUGGEST (AUTOCOMPLETE)
# =========================
def suggest_documents_query(query):

    if not query:
        return []

    cypher = """
    CALL db.index.fulltext.queryNodes($index, $query + "*")
    YIELD node, score

    WHERE node:Book OR node:Article OR node:Thesis

    RETURN
        node.id AS id,
        node.title AS title,
        labels(node)[0] AS type,
        score

    ORDER BY score DESC
    LIMIT 8
    """

    return neo4j_conn.query(
        cypher,
        {
            "index": FULLTEXT_INDEX,
            "query": query
        }
    )