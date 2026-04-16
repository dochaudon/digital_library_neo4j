from models.user_model import (
    create_user,
    find_user_by_email,
    get_all_users,
    get_user_by_id,
    delete_user,
    deactivate_user,
    update_user,
    change_password
)
from werkzeug.security import generate_password_hash, check_password_hash


# =========================
# REGISTER
# =========================
def register_user(data):

    if not data.get("email") or not data.get("password"):
        raise ValueError("Missing email or password")

    # hash password
    data["password"] = generate_password_hash(data["password"])

    result = create_user(data)

    if not result:
        raise ValueError("Email already exists")

    return result


# =========================
# LOGIN
# =========================
def login_user(email, password):

    user = find_user_by_email(email)

    if not user:
        return None

    if user.get("status") != "active":
        return None

    if not check_password_hash(user["password"], password):
        return None

    return user


# =========================
# GET USERS (ADMIN)
# =========================
def get_users_service():
    return get_all_users()


# =========================
# GET USER DETAIL
# =========================
def get_user_detail_service(user_id):
    return get_user_by_id(user_id)


# =========================
# UPDATE USER
# =========================
def update_user_service(user_id, data):

    user = get_user_by_id(user_id)
    if not user:
        raise ValueError("User not found")

    return update_user(user_id, data)


# =========================
# CHANGE PASSWORD
# =========================
def change_password_service(user_id, password):

    if not password:
        raise ValueError("Password is required")

    hashed = generate_password_hash(password)

    return change_password(user_id, hashed)


# =========================
# DEACTIVATE USER
# =========================
def deactivate_user_service(user_id):

    user = get_user_by_id(user_id)
    if not user:
        raise ValueError("User not found")

    if user.get("role") == "admin":
        raise ValueError("Cannot deactivate admin")

    if user.get("status") == "inactive":
        return user_id

    return deactivate_user(user_id)


# =========================
# DELETE USER
# =========================
def delete_user_service(user_id):

    user = get_user_by_id(user_id)
    if not user:
        raise ValueError("User not found")

    # không cho xóa admin
    if user.get("role") == "admin":
        raise ValueError("Cannot delete admin")

    return delete_user(user_id)