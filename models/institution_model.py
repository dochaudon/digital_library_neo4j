from database.neo4j_connection import neo4j_conn
import uuid

# =========================
# CREATE INSTITUTION
# =========================
def create_institution(data):
    name = data.get("name")
    inst_type = data.get("type")  # Publisher / University

    if not name or not inst_type:
        return None

    cypher = """
    CREATE (i:Institution {
        id: $id,
        name: $name,
        type: $type
    })
    RETURN i.id AS id, i.name AS name, i.type AS type
    """

    result = neo4j_conn.query(cypher, {
        "id": str(uuid.uuid4()),
        "name": name.strip(),
        "type": inst_type.strip()
    })

    return result[0] if result else None


# =========================
# GET ALL INSTITUTIONS
# =========================
def get_all_institutions():
    cypher = """
    MATCH (i:Institution)
    RETURN 
        i.id AS id, 
        i.name AS name, 
        i.type AS type
    ORDER BY i.name
    """

    return neo4j_conn.query(cypher)


# =========================
# GET INSTITUTION BY ID
# =========================
def get_institution_by_id(inst_id):
    cypher = """
    MATCH (i:Institution {id: $id})
    RETURN 
        i.id AS id, 
        i.name AS name, 
        i.type AS type
    """

    result = neo4j_conn.query(cypher, {"id": inst_id})
    return result[0] if result else None


# =========================
# UPDATE INSTITUTION
# =========================
def update_institution(inst_id, data):
    name = data.get("name")
    inst_type = data.get("type")

    if not name or not inst_type:
        return None

    cypher = """
    MATCH (i:Institution {id: $id})
    SET 
        i.name = $name,
        i.type = $type
    RETURN i.id AS id, i.name AS name, i.type AS type
    """

    result = neo4j_conn.query(cypher, {
        "id": inst_id,
        "name": name.strip(),
        "type": inst_type.strip()
    })

    return result[0] if result else None


# =========================
# DELETE INSTITUTION
# =========================
def delete_institution(inst_id):
    cypher = """
    MATCH (i:Institution {id: $id})
    DETACH DELETE i
    RETURN count(i) AS deleted
    """

    result = neo4j_conn.query(cypher, {"id": inst_id})
    return result[0]["deleted"] if result else 0