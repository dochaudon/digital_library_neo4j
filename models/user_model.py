from database.neo4j_connection import neo4j_conn
import uuid


# =========================
# CREATE USER
# =========================
def create_user(user_data):

    # check email tồn tại
    existing = find_user_by_email(user_data["email"])
    if existing:
        return None

    query = """
    CREATE (u:User {
        id: $id,
        username: $username,
        email: $email,
        password: $password,
        role: $role,
        status: 'active',
        created_at: datetime(),
        updated_at: datetime()
    })
    RETURN u.id AS id, u.email AS email
    """

    result = neo4j_conn.query(query, {
        "id": str(uuid.uuid4()),
        "username": user_data["username"],
        "email": user_data["email"],
        "password": user_data["password"],
        "role": user_data.get("role", "user")
    })

    return result[0] if result else None


# =========================
# FIND BY EMAIL
# =========================
def find_user_by_email(email):
    query = """
    MATCH (u:User {email: $email})
    RETURN u
    LIMIT 1
    """

    result = neo4j_conn.query(query, {"email": email})

    if not result:
        return None

    u = result[0]["u"]

    return {
        "id": u.get("id"),
        "username": u.get("username"),
        "email": u.get("email"),
        "password": u.get("password"),
        "role": u.get("role", "user"),
        "status": u.get("status", "active")
    }


# =========================
# GET USER BY ID
# =========================
def get_user_by_id(user_id):
    query = """
    MATCH (u:User {id: $id})
    RETURN u
    LIMIT 1
    """

    result = neo4j_conn.query(query, {"id": user_id})

    if not result:
        return None

    u = result[0]["u"]

    return {
        "id": u.get("id"),
        "username": u.get("username"),
        "email": u.get("email"),
        "role": u.get("role", "user"),
        "status": u.get("status", "active")
    }


# =========================
# GET ALL USERS (ADMIN)
# =========================
def get_all_users():
    query = """
    MATCH (u:User)
    RETURN u.id AS id,
           u.username AS username,
           u.email AS email,
           u.role AS role,
           u.status AS status,
           u.created_at AS created_at
    ORDER BY u.created_at DESC
    """

    return neo4j_conn.query(query)


# =========================
# UPDATE USER
# =========================
def update_user(user_id, data):

    query = """
    MATCH (u:User {id: $id})
    SET u.username = COALESCE($username, u.username),
        u.role = COALESCE($role, u.role),
        u.status = COALESCE($status, u.status),
        u.updated_at = datetime()
    RETURN u.id AS id
    """

    result = neo4j_conn.query(query, {
        "id": user_id,
        "username": data.get("username"),
        "role": data.get("role"),
        "status": data.get("status")
    })

    return result[0]["id"] if result else None


# =========================
# CHANGE PASSWORD
# =========================
def change_password(user_id, hashed_password):
    query = """
    MATCH (u:User {id: $id})
    SET u.password = $password,
        u.updated_at = datetime()
    RETURN u.id AS id
    """

    result = neo4j_conn.query(query, {
        "id": user_id,
        "password": hashed_password
    })

    return result[0]["id"] if result else None


# =========================
# DEACTIVATE USER (SOFT DELETE)
# =========================
def deactivate_user(user_id):
    query = """
    MATCH (u:User {id: $id})
    SET u.status = 'inactive',
        u.updated_at = datetime()
    RETURN u.id AS id
    """

    result = neo4j_conn.query(query, {"id": user_id})

    return result[0]["id"] if result else None


# =========================
# DELETE USER (HARD DELETE)
# =========================
def delete_user(user_id):
    query = """
    MATCH (u:User {id: $id})
    DETACH DELETE u
    RETURN COUNT(u) AS deleted
    """

    result = neo4j_conn.query(query, {"id": user_id})

    return result[0]["deleted"] if result else 0