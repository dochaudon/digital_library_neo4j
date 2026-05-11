from database.neo4j_connection import neo4j_conn

# =========================
# CREATE UNIVERSITY
# =========================
def create_university(data):
    name = data.get("name")

    if not name:
        return None

    cypher = """
    CREATE (u:University {
        id: $id,
        name: $name,
        address: $address,
        email: $email,
        phone: $phone,
        website: $website
    })
    RETURN u.id AS id, u.name AS name
    """

    result = neo4j_conn.query(cypher, {
        "id": data.get("id"),
        "name": name.strip(),
        "address": data.get("address"),
        "email": data.get("email"),
        "phone": data.get("phone"),
        "website": data.get("website")
    })

    return result[0] if result else None


# =========================
# GET ALL UNIVERSITIES
# =========================
def get_all_universities(q=None):
    if q:
        cypher = """
        MATCH (u:University)
        WHERE toLower(u.name) CONTAINS toLower($q)
        RETURN 
            u.id AS id, 
            u.name AS name
        ORDER BY u.name
        """
        return neo4j_conn.query(cypher, {"q": q})

    cypher = """
    MATCH (u:University)
    RETURN 
        u.id AS id, 
        u.name AS name
    ORDER BY u.name
    """

    return neo4j_conn.query(cypher)


# =========================
# GET UNIVERSITY BY ID
# =========================
def get_university_by_id(uni_id):
    cypher = """
    MATCH (u:University {id: $id})
    RETURN 
        u.id AS id, 
        u.name AS name,
        u.address AS address,
        u.email AS email,
        u.phone AS phone,
        u.website AS website
    """

    result = neo4j_conn.query(cypher, {"id": uni_id})
    return result[0] if result else None


# =========================
# UPDATE UNIVERSITY
# =========================
def update_university(uni_id, data):
    name = data.get("name")

    if not name:
        return None

    cypher = """
    MATCH (u:University {id: $id})
    SET u.name = $name,
        u.address = $address,
        u.email = $email,
        u.phone = $phone,
        u.website = $website
    RETURN u.id AS id, u.name AS name
    """

    result = neo4j_conn.query(cypher, {
        "id": uni_id,
        "name": name.strip(),
        "address": data.get("address"),
        "email": data.get("email"),
        "phone": data.get("phone"),
        "website": data.get("website")
    })

    return result[0] if result else None


# =========================
# DELETE UNIVERSITY
# =========================
def delete_university(uni_id):
    cypher = """
    MATCH (u:University {id: $id})
    DETACH DELETE u
    RETURN count(u) AS deleted
    """

    result = neo4j_conn.query(cypher, {"id": uni_id})
    return result[0]["deleted"] if result else 0
