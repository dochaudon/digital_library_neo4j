from database.neo4j_connection import neo4j_conn

def get_thesis_by_id(id):
    query = """
    MATCH (t:Thesis {id:$id})
    OPTIONAL MATCH (t)-[:WRITTEN_BY]->(a:Author)
    OPTIONAL MATCH (t)-[:SUBMITTED_TO]->(u:University)

    RETURN 
        t.id AS id,
        t.title AS title,
        t.year AS year,
        t.degree AS degree,
        u.name AS university,
        collect(a.name) AS authors
    """
    result = neo4j_conn.query(query, {"id": id})
    return result[0] if result else None