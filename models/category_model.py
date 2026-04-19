from database.neo4j_connection import neo4j_conn
import uuid

# =========================
# CREATE CATEGORY
# =========================
def create_category(data):
    name = data.get("name")

    if not name:
        return None

    cypher = """
    CREATE (c:Category {
        id: $id,
        name: $name
    })
    RETURN c.id AS id, c.name AS name
    """

    result = neo4j_conn.query(cypher, {
        "id": str(uuid.uuid4()),
        "name": name.strip()
    })

    return result[0] if result else None


# =========================
# GET ALL CATEGORIES
# =========================
def get_all_categories():
    cypher = """
    MATCH (c:Category)
    RETURN 
        c.id AS id, 
        c.name AS name
    ORDER BY c.name
    """

    return neo4j_conn.query(cypher)


# =========================
# GET CATEGORY BY ID
# =========================
def get_category_by_id(category_id):
    cypher = """
    MATCH (c:Category {id: $id})
    RETURN 
        c.id AS id, 
        c.name AS name
    """

    result = neo4j_conn.query(cypher, {"id": category_id})
    return result[0] if result else None


# =========================
# UPDATE CATEGORY
# =========================
def update_category(category_id, data):
    name = data.get("name")

    if not name:
        return None

    cypher = """
    MATCH (c:Category {id: $id})
    SET c.name = $name
    RETURN c.id AS id, c.name AS name
    """

    result = neo4j_conn.query(cypher, {
        "id": category_id,
        "name": name.strip()
    })

    return result[0] if result else None


# =========================
# DELETE CATEGORY
# =========================
def delete_category(category_id):
    cypher = """
    MATCH (c:Category {id: $id})
    DETACH DELETE c
    RETURN count(c) AS deleted
    """

    result = neo4j_conn.query(cypher, {"id": category_id})
    return result[0]["deleted"] if result else 0