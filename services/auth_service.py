import uuid
from flask_jwt_extended import create_access_token
from models.user_model import create_user, find_user_by_email
from services.auth_utils import hash_password, check_password


def register_user(data):

    # check email tồn tại
    if find_user_by_email(data["email"]):
        return {"error": "Email already exists"}

    user_data = {
        "id": str(uuid.uuid4()),
        "username": data["username"],
        "email": data["email"],
        "password": hash_password(data["password"]),
        "role": "user"
    }

    create_user(user_data)

    return {"message": "Register success"}

def login_user(data):

    user = find_user_by_email(data["email"])

    if not user:
        return {"error": "User not found"}

    if not user.get("password"):
        return {"error": "Invalid user data"}

    if not check_password(user["password"], data["password"]):
        return {"error": "Wrong password"}

    token = create_access_token(identity=user["id"])

    return {
        "token": token,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"]
        }
    }