from database.neo4j_connection import neo4j_conn
import uuid


def create_author(data):
    cypher = """
    CREATE (a:Author {
        id: $id,
        name: $name
    })
    RETURN a.id AS id
    """
    return neo4j_conn.query(cypher, {
        "id": str(uuid.uuid4()),
        "name": data.get("name")
    })


def get_all_authors():
    cypher = """
    MATCH (a:Author)
    RETURN a.id AS id, a.name AS name
    ORDER BY a.name
    """
    return neo4j_conn.query(cypher)


def get_author_by_id(id):
    cypher = """
    MATCH (a:Author {id: $id})
    RETURN a.id AS id, a.name AS name
    """
    result = neo4j_conn.query(cypher, {"id": id})
    return result[0] if result else None


def update_author(id, data):
    cypher = """
    MATCH (a:Author {id: $id})
    SET a.name = $name
    """
    neo4j_conn.query(cypher, {
        "id": id,
        "name": data.get("name")
    })


def delete_author(id):
    cypher = """
    MATCH (a:Author {id: $id})
    DETACH DELETE a
    """
    neo4j_conn.query(cypher, {"id": id})