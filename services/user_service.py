from models.user_model import (
    get_all_users,
    get_user_by_id,
    delete_user,
    deactivate_user,
    update_user,
    change_password
)

from werkzeug.security import generate_password_hash


# =========================
# GET ALL USERS (ADMIN)
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
        return {"error": "User not found"}

    return {
        "id": update_user(user_id, data)
    }


# =========================
# CHANGE PASSWORD
# =========================
def change_password_service(user_id, password):

    if not password:
        return {"error": "Password is required"}

    user = get_user_by_id(user_id)
    if not user:
        return {"error": "User not found"}

    hashed = generate_password_hash(password)

    return {
        "id": change_password(user_id, hashed)
    }


# =========================
# DEACTIVATE USER (SOFT DELETE)
# =========================
def deactivate_user_service(user_id):

    user = get_user_by_id(user_id)
    if not user:
        return {"error": "User not found"}

    if user.get("role") == "admin":
        return {"error": "Cannot deactivate admin"}

    if user.get("status") == "inactive":
        return {"message": "User already inactive"}

    return {
        "id": deactivate_user(user_id)
    }


# =========================
# DELETE USER (HARD DELETE)
# =========================
def delete_user_service(user_id):

    user = get_user_by_id(user_id)
    if not user:
        return {"error": "User not found"}

    if user.get("role") == "admin":
        return {"error": "Cannot delete admin"}

    deleted = delete_user(user_id)

    return {
        "deleted": deleted
    }