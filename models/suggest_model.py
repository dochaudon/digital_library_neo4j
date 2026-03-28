from database.neo4j_connection import neo4j_conn

def suggest_documents_query(query):

    cypher = """
    MATCH (d)
    WHERE (d:Book OR d:Article OR d:Thesis)
      AND toLower(d.title) CONTAINS toLower($q)

    RETURN 
        d.id AS id,
        d.title AS title,
        labels(d)[0] AS type

    LIMIT 8
    """

    return neo4j_conn.query(cypher, {"q": query})