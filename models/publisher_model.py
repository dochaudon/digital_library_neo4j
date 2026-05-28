from database.neo4j_connection import neo4j_conn

# =========================
# CREATE PUBLISHER
# =========================
def create_publisher(data):
    name = data.get("name")

    if not name:
        return None

    cypher = """
    CREATE (p:Publisher {
        id: $id,
        name: $name
    })
    RETURN p.id AS id, p.name AS name
    """

    result = neo4j_conn.query(cypher, {
        "id": data.get("id"),
        "name": name.strip()
    })

    return result[0] if result else None


# =========================
# GET ALL PUBLISHERS
# =========================
def get_all_publishers(q=None):
    if q:
        cypher = """
        MATCH (p:Publisher)
        WHERE toLower(p.name) CONTAINS toLower($q)
        RETURN 
            p.id AS id, 
            p.name AS name
        ORDER BY toInteger(substring(p.id, 1)) DESC
        """
        return neo4j_conn.query(cypher, {"q": q})

    cypher = """
    MATCH (p:Publisher)
    RETURN 
        p.id AS id, 
        p.name AS name
    ORDER BY toInteger(substring(p.id, 1)) DESC
    """

    return neo4j_conn.query(cypher)


# =========================
# GET PUBLISHER BY ID
# =========================
def get_publisher_by_id(pub_id):
    cypher = """
    MATCH (p:Publisher {id: $id})
    RETURN 
        p.id AS id, 
        p.name AS name
    """

    result = neo4j_conn.query(cypher, {"id": pub_id})
    return result[0] if result else None


# =========================
# UPDATE PUBLISHER
# =========================
def update_publisher(pub_id, data):
    name = data.get("name")

    if not name:
        return None

    cypher = """
    MATCH (p:Publisher {id: $id})
    SET p.name = $name
    RETURN p.id AS id, p.name AS name
    """

    result = neo4j_conn.query(cypher, {
        "id": pub_id,
        "name": name.strip()
    })

    return result[0] if result else None


# =========================
# DELETE PUBLISHER
# =========================
def delete_publisher(pub_id):
    cypher = """
    MATCH (p:Publisher {id: $id})
    DETACH DELETE p
    RETURN count(p) AS deleted
    """

    result = neo4j_conn.query(cypher, {"id": pub_id})
    return result[0]["deleted"] if result else 0
