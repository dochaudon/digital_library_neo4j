from database.neo4j_connection import neo4j_conn
import uuid

# =========================
# CREATE LANGUAGE
# =========================
def create_language(data):
    name = data.get("name")

    if not name:
        return None

    cypher = """
    CREATE (l:Language {
        id: $id,
        name: $name
    })
    RETURN l.id AS id, l.name AS name
    """

    result = neo4j_conn.query(cypher, {
        "id": str(uuid.uuid4()),
        "name": name.strip()
    })

    return result[0] if result else None


# =========================
# GET ALL LANGUAGES
# =========================
def get_all_languages():
    cypher = """
    MATCH (l:Language)
    RETURN 
        l.id AS id, 
        l.name AS name
    ORDER BY l.name
    """

    return neo4j_conn.query(cypher)


# =========================
# GET LANGUAGE BY ID
# =========================
def get_language_by_id(language_id):
    cypher = """
    MATCH (l:Language {id: $id})
    RETURN 
        l.id AS id, 
        l.name AS name
    """

    result = neo4j_conn.query(cypher, {"id": language_id})
    return result[0] if result else None


# =========================
# UPDATE LANGUAGE
# =========================
def update_language(language_id, data):
    name = data.get("name")

    if not name:
        return None

    cypher = """
    MATCH (l:Language {id: $id})
    SET l.name = $name
    RETURN l.id AS id, l.name AS name
    """

    result = neo4j_conn.query(cypher, {
        "id": language_id,
        "name": name.strip()
    })

    return result[0] if result else None


# =========================
# DELETE LANGUAGE
# =========================
def delete_language(language_id):
    cypher = """
    MATCH (l:Language {id: $id})
    DETACH DELETE l
    RETURN count(l) AS deleted
    """

    result = neo4j_conn.query(cypher, {"id": language_id})
    return result[0]["deleted"] if result else 0