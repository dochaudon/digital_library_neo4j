import uuid
from flask_jwt_extended import create_access_token

from models.user_model import create_user, find_user_by_email
from services.auth_utils import hash_password, check_password


# =========================
# CLEAN INPUT
# =========================
def clean(value):
    return value.strip() if value else None


def normalize_email(email):
    return email.strip().lower() if email else None


# =========================
# REGISTER
# =========================
def register_user(data):

    username = clean(data.get("username"))
    email = normalize_email(data.get("email"))
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
        result = create_user(user_data)

        if not result:
            return {"error": "User creation failed"}

        return {"message": "Register success"}

    except Exception as e:
        print("REGISTER ERROR:", e)
        return {"error": "Register failed"}


# =========================
# LOGIN
# =========================
def login_user(data):

    email = normalize_email(data.get("email"))
    password = data.get("password")

    # validate
    if not email or not password:
        return {"error": "Missing email or password"}

    user = find_user_by_email(email)

    if not user:
        return {"error": "User not found"}

    if not user.get("password"):
        return {"error": "Invalid user data"}

    # check password
    if not check_password(user["password"], password):
        return {"error": "Wrong password"}

    # check status
    if user.get("status") != "active":
        return {"error": "Account is inactive"}

    try:
        token = create_access_token(identity=user["id"])
    except Exception as e:
        print("TOKEN ERROR:", e)
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