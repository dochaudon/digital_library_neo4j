from database.neo4j_connection import neo4j_conn
import uuid

# =========================
# CREATE KEYWORD
# =========================
def create_keyword(data):
    name = data.get("name")

    if not name:
        return None

    cypher = """
    CREATE (k:Keyword {
        id: $id,
        name: $name
    })
    RETURN k.id AS id, k.name AS name
    """

    result = neo4j_conn.query(cypher, {
        "id": str(uuid.uuid4()),
        "name": name.strip()
    })

    return result[0] if result else None


# =========================
# GET ALL KEYWORDS
# =========================
def get_all_keywords():
    cypher = """
    MATCH (k:Keyword)
    RETURN 
        k.id AS id, 
        k.name AS name
    ORDER BY k.name
    """

    return neo4j_conn.query(cypher)


# =========================
# GET KEYWORD BY ID
# =========================
def get_keyword_by_id(keyword_id):
    cypher = """
    MATCH (k:Keyword {id: $id})
    RETURN 
        k.id AS id, 
        k.name AS name
    """

    result = neo4j_conn.query(cypher, {"id": keyword_id})
    return result[0] if result else None


# =========================
# UPDATE KEYWORD
# =========================
def update_keyword(keyword_id, data):
    name = data.get("name")

    if not name:
        return None

    cypher = """
    MATCH (k:Keyword {id: $id})
    SET k.name = $name
    RETURN k.id AS id, k.name AS name
    """

    result = neo4j_conn.query(cypher, {
        "id": keyword_id,
        "name": name.strip()
    })

    return result[0] if result else None


# =========================
# DELETE KEYWORD
# =========================
def delete_keyword(keyword_id):
    cypher = """
    MATCH (k:Keyword {id: $id})
    DETACH DELETE k
    RETURN count(k) AS deleted
    """

    result = neo4j_conn.query(cypher, {"id": keyword_id})
    return result[0]["deleted"] if result else 0