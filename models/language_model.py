from database.neo4j_connection import neo4j_conn
import uuid


def create_language(data):
    cypher = """
    CREATE (l:Language {
        id: $id,
        name: $name
    })
    RETURN l.id AS id
    """
    return neo4j_conn.query(cypher, {
        "id": str(uuid.uuid4()),
        "name": data.get("name")
    })


def get_all_languages():
    cypher = """
    MATCH (l:Language)
    RETURN l.id AS id, l.name AS name
    ORDER BY l.name
    """
    return neo4j_conn.query(cypher)


def get_language_by_id(id):
    cypher = """
    MATCH (l:Language {id: $id})
    RETURN l.id AS id, l.name AS name
    """
    result = neo4j_conn.query(cypher, {"id": id})
    return result[0] if result else None


def update_language(id, data):
    cypher = """
    MATCH (l:Language {id: $id})
    SET l.name = $name
    """
    neo4j_conn.query(cypher, {
        "id": id,
        "name": data.get("name")
    })


def delete_language(id):
    cypher = """
    MATCH (l:Language {id: $id})
    DETACH DELETE l
    """
    neo4j_conn.query(cypher, {"id": id})