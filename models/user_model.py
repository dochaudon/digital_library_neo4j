from database.neo4j_connection import neo4j_conn


def create_user(user_data):
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
    return neo4j_conn.query(query, user_data)


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
        "role": user_node.get("role", "user")
    }