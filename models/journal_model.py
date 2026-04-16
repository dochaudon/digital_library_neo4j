from database.neo4j_connection import neo4j_conn
import uuid


def create_journal(data):
    cypher = """
    CREATE (j:Journal {
        id: $id,
        name: $name
    })
    RETURN j.id AS id
    """
    return neo4j_conn.query(cypher, {
        "id": str(uuid.uuid4()),
        "name": data.get("name")
    })


def get_all_journals():
    cypher = """
    MATCH (j:Journal)
    RETURN j.id AS id, j.name AS name
    ORDER BY j.name
    """
    return neo4j_conn.query(cypher)


def get_journal_by_id(id):
    cypher = """
    MATCH (j:Journal {id: $id})
    RETURN j.id AS id, j.name AS name
    """
    result = neo4j_conn.query(cypher, {"id": id})
    return result[0] if result else None


def update_journal(id, data):
    cypher = """
    MATCH (j:Journal {id: $id})
    SET j.name = $name
    """
    neo4j_conn.query(cypher, {
        "id": id,
        "name": data.get("name")
    })


def delete_journal(id):
    cypher = """
    MATCH (j:Journal {id: $id})
    DETACH DELETE j
    """
    neo4j_conn.query(cypher, {"id": id})