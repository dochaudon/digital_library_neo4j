import uuid
from flask_jwt_extended import create_access_token

from models.user_model import create_user, find_user_by_email
from services.auth_utils import hash_password, check_password


# =========================
# CLEAN INPUT
# =========================
def clean(value):
    if not value:
        return None
    return value.strip()


# =========================
# REGISTER
# =========================
def register_user(data):

    username = clean(data.get("username"))
    email = clean(data.get("email"))
    password = data.get("password")

    # validate
    if not username or not email or not password:
        return {"error": "Missing required fields"}

    # check email tồn tại
    if find_user_by_email(email):
        return {"error": "Email already exists"}

    user_data = {
        "id": str(uuid.uuid4()),
        "username": username,
        "email": email,
        "password": hash_password(password),
        "role": "user"
    }

    try:
        create_user(user_data)
        return {"message": "Register success"}
    except Exception:
        return {"error": "Register failed"}


# =========================
# LOGIN
# =========================
def login_user(data):

    email = clean(data.get("email"))
    password = data.get("password")

    # validate
    if not email or not password:
        return {"error": "Missing email or password"}

    user = find_user_by_email(email)

    if not user:
        return {"error": "User not found"}

    if not user.get("password"):
        return {"error": "Invalid user data"}

    if not check_password(user["password"], password):
        return {"error": "Wrong password"}

    try:
        token = create_access_token(identity=user["id"])
    except Exception:
        return {"error": "Token creation failed"}

    return {
        "message": "Login success",
        "token": token,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"]
        }
    }