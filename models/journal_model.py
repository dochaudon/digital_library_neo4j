from database.neo4j_connection import neo4j_conn
import uuid

# =========================
# CREATE JOURNAL
# =========================
def create_journal(data):
    name = data.get("name")

    if not name:
        return None

    cypher = """
    CREATE (j:Journal {
        id: $id,
        name: $name
    })
    RETURN j.id AS id, j.name AS name
    """

    result = neo4j_conn.query(cypher, {
        "id": str(uuid.uuid4()),
        "name": name.strip()
    })

    return result[0] if result else None


# =========================
# GET ALL JOURNALS
# =========================
def get_all_journals():
    cypher = """
    MATCH (j:Journal)
    RETURN 
        j.id AS id, 
        j.name AS name
    ORDER BY j.name
    """

    return neo4j_conn.query(cypher)


# =========================
# GET JOURNAL BY ID
# =========================
def get_journal_by_id(journal_id):
    cypher = """
    MATCH (j:Journal {id: $id})
    RETURN 
        j.id AS id, 
        j.name AS name
    """

    result = neo4j_conn.query(cypher, {"id": journal_id})
    return result[0] if result else None


# =========================
# UPDATE JOURNAL
# =========================
def update_journal(journal_id, data):
    name = data.get("name")

    if not name:
        return None

    cypher = """
    MATCH (j:Journal {id: $id})
    SET j.name = $name
    RETURN j.id AS id, j.name AS name
    """

    result = neo4j_conn.query(cypher, {
        "id": journal_id,
        "name": name.strip()
    })

    return result[0] if result else None


# =========================
# DELETE JOURNAL
# =========================
def delete_journal(journal_id):
    cypher = """
    MATCH (j:Journal {id: $id})
    DETACH DELETE j
    RETURN count(j) AS deleted
    """

    result = neo4j_conn.query(cypher, {"id": journal_id})
    return result[0]["deleted"] if result else 0