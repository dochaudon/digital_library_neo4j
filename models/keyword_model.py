from database.neo4j_connection import neo4j_conn
import uuid


def create_keyword(data):
    cypher = """
    CREATE (k:Keyword {
        id: $id,
        name: $name
    })
    RETURN k.id AS id
    """
    return neo4j_conn.query(cypher, {
        "id": str(uuid.uuid4()),
        "name": data.get("name")
    })


def get_all_keywords():
    cypher = """
    MATCH (k:Keyword)
    RETURN k.id AS id, k.name AS name
    ORDER BY k.name
    """
    return neo4j_conn.query(cypher)


def get_keyword_by_id(id):
    cypher = """
    MATCH (k:Keyword {id: $id})
    RETURN k.id AS id, k.name AS name
    """
    result = neo4j_conn.query(cypher, {"id": id})
    return result[0] if result else None


def update_keyword(id, data):
    cypher = """
    MATCH (k:Keyword {id: $id})
    SET k.name = $name
    """
    neo4j_conn.query(cypher, {
        "id": id,
        "name": data.get("name")
    })


def delete_keyword(id):
    cypher = """
    MATCH (k:Keyword {id: $id})
    DETACH DELETE k
    """
    neo4j_conn.query(cypher, {"id": id})