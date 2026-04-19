from database.neo4j_connection import neo4j_conn
import uuid

# =========================
# CREATE AUTHOR
# =========================
def create_author(data):
    name = data.get("name")

    if not name:
        return None

    cypher = """
    CREATE (a:Author {
        id: $id,
        name: $name
    })
    RETURN a.id AS id, a.name AS name
    """

    result = neo4j_conn.query(cypher, {
        "id": str(uuid.uuid4()),
        "name": name.strip()
    })

    return result[0] if result else None


# =========================
# GET ALL AUTHORS
# =========================
def get_all_authors():
    cypher = """
    MATCH (a:Author)
    RETURN 
        a.id AS id, 
        a.name AS name
    ORDER BY a.name
    """

    return neo4j_conn.query(cypher)


# =========================
# GET AUTHOR BY ID
# =========================
def get_author_by_id(author_id):
    cypher = """
    MATCH (a:Author {id: $id})
    RETURN 
        a.id AS id, 
        a.name AS name
    """

    result = neo4j_conn.query(cypher, {"id": author_id})
    return result[0] if result else None


# =========================
# UPDATE AUTHOR
# =========================
def update_author(author_id, data):
    name = data.get("name")

    if not name:
        return None

    cypher = """
    MATCH (a:Author {id: $id})
    SET a.name = $name
    RETURN a.id AS id, a.name AS name
    """

    result = neo4j_conn.query(cypher, {
        "id": author_id,
        "name": name.strip()
    })

    return result[0] if result else None


# =========================
# DELETE AUTHOR
# =========================
def delete_author(author_id):
    cypher = """
    MATCH (a:Author {id: $id})
    DETACH DELETE a
    RETURN count(a) AS deleted
    """

    result = neo4j_conn.query(cypher, {"id": author_id})
    return result[0]["deleted"] if result else 0