from models.user_model import (
    get_all_users,
    get_user_by_id,
    delete_user,
    deactivate_user,
    update_user,
    change_password
)



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

    from services.auth_utils import hash_password
    hashed = hash_password(password)

    return {
        "id": change_password(user_id, hashed)
    }



# =========================
# TOGGLE STATUS (BAN / UNBAN)
# =========================
def toggle_status_service(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return {"error": "User not found"}

    if user.get("role") == "admin":
        return {"error": "Cannot ban admin"}

    new_status = "active" if user.get("status") == "inactive" else "inactive"
    
    return {
        "id": update_user(user_id, {"status": new_status}),
        "new_status": new_status
    }


# =========================
# TOGGLE ROLE (ADMIN / USER)
# =========================
def toggle_role_service(user_id):
    user = get_user_by_id(user_id)
    if not user:
        return {"error": "User not found"}

    new_role = "user" if user.get("role") == "admin" else "admin"
    
    return {
        "id": update_user(user_id, {"role": new_role}),
        "new_role": new_role
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