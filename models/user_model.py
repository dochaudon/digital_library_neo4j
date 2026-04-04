from database.neo4j_connection import neo4j_conn
import hashlib
import uuid


# =========================
# HASH PASSWORD
# =========================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()


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
        created_at: datetime()
    })
    RETURN u
    """

    params = {
        "id": str(uuid.uuid4()),
        "username": user_data["username"],
        "email": user_data["email"],
        "password": hash_password(user_data["password"]),
        "role": user_data.get("role", "user")
    }

    return neo4j_conn.query(query, params)


# =========================
# FIND BY EMAIL
# =========================
def find_user_by_email(email):
    query = """
    MATCH (u:User {email: $email})
    RETURN u
    """
    result = neo4j_conn.query(query, {"email": email})

    if not result:
        return None

    user_node = result[0]["u"]

    return {
        "id": user_node["id"],
        "username": user_node["username"],
        "email": user_node["email"],
        "password": user_node["password"],
        "role": user_node.get("role", "user"),
        "status": user_node.get("status", "active")
    }


# =========================
# LOGIN
# =========================
def login_user(email, password):

    user = find_user_by_email(email)

    if not user:
        return None

    hashed = hash_password(password)

    if user["password"] != hashed:
        return None

    if user["status"] != "active":
        return None

    return user


# =========================
# GET USER BY ID
# =========================
def get_user_by_id(user_id):
    query = """
    MATCH (u:User {id: $id})
    RETURN u
    """
    result = neo4j_conn.query(query, {"id": user_id})

    if not result:
        return None

    u = result[0]["u"]

    return {
        "id": u["id"],
        "username": u["username"],
        "email": u["email"],
        "role": u.get("role", "user"),
        "status": u.get("status", "active")
    }


# =========================
# UPDATE USER
# =========================
def update_user(user_id, data):
    query = """
    MATCH (u:User {id: $id})
    SET u.username = $username
    RETURN u
    """

    return neo4j_conn.query(query, {
        "id": user_id,
        "username": data["username"]
    })


# =========================
# CHANGE PASSWORD
# =========================
def change_password(user_id, new_password):
    query = """
    MATCH (u:User {id: $id})
    SET u.password = $password
    RETURN u
    """

    return neo4j_conn.query(query, {
        "id": user_id,
        "password": hash_password(new_password)
    })


# =========================
# DEACTIVATE USER
# =========================
def deactivate_user(user_id):
    query = """
    MATCH (u:User {id: $id})
    SET u.status = 'inactive'
    RETURN u
    """

    return neo4j_conn.query(query, {"id": user_id})