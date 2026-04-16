from database.neo4j_connection import neo4j_conn
import uuid


def create_institution(data):
    cypher = """
    CREATE (i:Institution {
        id: $id,
        name: $name,
        type: $type
    })
    RETURN i.id AS id
    """
    return neo4j_conn.query(cypher, {
        "id": str(uuid.uuid4()),
        "name": data.get("name"),
        "type": data.get("type")  # Publisher / University
    })


def get_all_institutions():
    cypher = """
    MATCH (i:Institution)
    RETURN i.id AS id, i.name AS name, i.type AS type
    ORDER BY i.name
    """
    return neo4j_conn.query(cypher)


def get_institution_by_id(id):
    cypher = """
    MATCH (i:Institution {id: $id})
    RETURN i.id AS id, i.name AS name, i.type AS type
    """
    result = neo4j_conn.query(cypher, {"id": id})
    return result[0] if result else None


def update_institution(id, data):
    cypher = """
    MATCH (i:Institution {id: $id})
    SET i.name = $name,
        i.type = $type
    """
    neo4j_conn.query(cypher, {
        "id": id,
        "name": data.get("name"),
        "type": data.get("type")
    })


def delete_institution(id):
    cypher = """
    MATCH (i:Institution {id: $id})
    DETACH DELETE i
    """
    neo4j_conn.query(cypher, {"id": id})