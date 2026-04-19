from database.neo4j_connection import neo4j_conn
import uuid

# =========================
# CREATE SUBJECT
# =========================
def create_subject(data):
    name = data.get("name")

    if not name:
        return None

    cypher = """
    CREATE (s:Subject {
        id: $id,
        name: $name
    })
    RETURN s.id AS id, s.name AS name
    """

    result = neo4j_conn.query(cypher, {
        "id": str(uuid.uuid4()),
        "name": name.strip()
    })

    return result[0] if result else None


# =========================
# GET ALL SUBJECTS
# =========================
def get_all_subjects():
    cypher = """
    MATCH (s:Subject)
    RETURN 
        s.id AS id, 
        s.name AS name
    ORDER BY s.name
    """

    return neo4j_conn.query(cypher)


# =========================
# GET SUBJECT BY ID
# =========================
def get_subject_by_id(subject_id):
    cypher = """
    MATCH (s:Subject {id: $id})
    RETURN 
        s.id AS id, 
        s.name AS name
    """

    result = neo4j_conn.query(cypher, {"id": subject_id})
    return result[0] if result else None


# =========================
# UPDATE SUBJECT
# =========================
def update_subject(subject_id, data):
    name = data.get("name")

    if not name:
        return None

    cypher = """
    MATCH (s:Subject {id: $id})
    SET s.name = $name
    RETURN s.id AS id, s.name AS name
    """

    result = neo4j_conn.query(cypher, {
        "id": subject_id,
        "name": name.strip()
    })

    return result[0] if result else None


# =========================
# DELETE SUBJECT
# =========================
def delete_subject(subject_id):
    cypher = """
    MATCH (s:Subject {id: $id})
    DETACH DELETE s
    RETURN count(s) AS deleted
    """

    result = neo4j_conn.query(cypher, {"id": subject_id})
    return result[0]["deleted"] if result else 0