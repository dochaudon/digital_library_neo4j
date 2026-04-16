from database.neo4j_connection import neo4j_conn
import uuid


def create_category(data):
    cypher = """
    CREATE (c:Category {
        id: $id,
        name: $name
    })
    RETURN c.id AS id
    """
    return neo4j_conn.query(cypher, {
        "id": str(uuid.uuid4()),
        "name": data.get("name")
    })


def get_all_categories():
    cypher = """
    MATCH (c:Category)
    RETURN c.id AS id, c.name AS name
    ORDER BY c.name
    """
    return neo4j_conn.query(cypher)


def get_category_by_id(id):
    cypher = """
    MATCH (c:Category {id: $id})
    RETURN c.id AS id, c.name AS name
    """
    result = neo4j_conn.query(cypher, {"id": id})
    return result[0] if result else None


def update_category(id, data):
    cypher = """
    MATCH (c:Category {id: $id})
    SET c.name = $name
    """
    neo4j_conn.query(cypher, {
        "id": id,
        "name": data.get("name")
    })


def delete_category(id):
    cypher = """
    MATCH (c:Category {id: $id})
    DETACH DELETE c
    """
    neo4j_conn.query(cypher, {"id": id})