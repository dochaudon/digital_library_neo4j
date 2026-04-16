from database.neo4j_connection import neo4j_conn
import uuid


def create_subject(data):
    cypher = """
    CREATE (s:Subject {
        id: $id,
        name: $name
    })
    RETURN s.id AS id
    """
    return neo4j_conn.query(cypher, {
        "id": str(uuid.uuid4()),
        "name": data.get("name")
    })


def get_all_subjects():
    cypher = """
    MATCH (s:Subject)
    RETURN s.id AS id, s.name AS name
    ORDER BY s.name
    """
    return neo4j_conn.query(cypher)


def get_subject_by_id(id):
    cypher = """
    MATCH (s:Subject {id: $id})
    RETURN s.id AS id, s.name AS name
    """
    result = neo4j_conn.query(cypher, {"id": id})
    return result[0] if result else None


def update_subject(id, data):
    cypher = """
    MATCH (s:Subject {id: $id})
    SET s.name = $name
    """
    neo4j_conn.query(cypher, {
        "id": id,
        "name": data.get("name")
    })


def delete_subject(id):
    cypher = """
    MATCH (s:Subject {id: $id})
    DETACH DELETE s
    """
    neo4j_conn.query(cypher, {"id": id})